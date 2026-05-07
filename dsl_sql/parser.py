from typing import List, Optional, Tuple

from .constants import DIRECTORS, FIELD_WORDS, GENRES
from .models import Node, ParseError, QuerySpec, Token, YearCondition


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.spec = QuerySpec()

    def current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def current_type(self) -> Optional[str]:
        tok = self.current()
        return None if tok is None else tok.token_type

    def advance(self) -> Optional[Token]:
        tok = self.current()
        if tok is not None:
            self.pos += 1
        return tok

    def expect(self, token_type: str, expected: Optional[List[str]] = None) -> Token:
        tok = self.current()
        if tok is None:
            raise ParseError(
                message=f"Ожидался токен типа {token_type}, но запрос закончился.",
                token=None,
                expected=expected or [token_type],
            )
        if tok.token_type != token_type:
            raise ParseError(
                message=f"Ожидался токен типа {token_type}, но получен {tok.token_type}.",
                token=tok,
                expected=expected or [token_type],
            )
        self.pos += 1
        return tok

    def parse(self) -> Tuple[Node, QuerySpec]:
        root = self.parse_query()
        if self.current() is not None:
            raise ParseError(
                message="Обнаружены лишние токены после завершения корректного запроса.",
                token=self.current(),
                expected=["конец запроса"],
            )
        return root, self.spec

    def parse_query(self) -> Node:
        node = Node("Запрос")
        node.add(self.parse_command())

        if self.current_type() == "QUANTIFIER":
            node.add(self.parse_quantifier())

        node.add(self.parse_object())

        tail = self.parse_filters_opt()
        if tail is not None:
            node.add(tail)

        clauses = self.parse_clauses_opt()
        if clauses is not None:
            node.add(clauses)

        return node

    def parse_command(self) -> Node:
        tok = self.expect("COMMAND", ["найти", "показать", "вывести"])
        return Node("Команда", tok.value)

    def parse_quantifier(self) -> Node:
        tok = self.expect("QUANTIFIER", ["весь"])
        return Node("Квантор", tok.value)

    def parse_object(self) -> Node:
        tok = self.expect("OBJECT", ["фильм", "сериал", "мультфильм"])
        self.spec.object_type = tok.value
        return Node("Объект", tok.value)

    def parse_filters_opt(self) -> Optional[Node]:
        tok = self.current()
        if tok is None:
            return None

        if tok.token_type not in {"BY", "DIRECTOR", "YEAR", "AFTER", "BEFORE", "FROM"}:
            return None

        tail = Node("Фильтры")

        if tok.token_type == "BY":
            tail.add(self.parse_genre_filter())
            if self.current_type() in {"YEAR", "AFTER", "BEFORE", "FROM"}:
                tail.add(self.parse_year_filter())
            return tail

        if tok.token_type == "DIRECTOR":
            tail.add(self.parse_director_filter())
            if self.current_type() in {"YEAR", "AFTER", "BEFORE", "FROM"}:
                tail.add(self.parse_year_filter())
            return tail

        if tok.token_type in {"YEAR", "AFTER", "BEFORE", "FROM"}:
            tail.add(self.parse_year_filter())
            return tail

        return None

    def parse_clauses_opt(self) -> Optional[Node]:
        tok = self.current()
        if tok is None:
            return None

        if tok.token_type not in {"GROUP", "HAVING", "ORDER"}:
            return None

        node = Node("SQLКлаузы")

        if self.current_type() == "GROUP":
            node.add(self.parse_group_by_clause())

        if self.current_type() == "HAVING":
            node.add(self.parse_having_clause())

        if self.current_type() == "ORDER":
            node.add(self.parse_order_by_clause())

        if self.current() is not None and self.current_type() in {"GROUP", "HAVING", "ORDER"}:
            raise ParseError(
                message="Клаузы должны идти в порядке: GROUP BY, HAVING, ORDER BY.",
                token=self.current(),
                expected=["конец запроса"],
            )

        return node

    def parse_group_by_clause(self) -> Node:
        node = Node("GroupBy")
        self.expect("GROUP", ["группировать"])
        node.add(Node("Оператор", "группировать"))
        self.expect("BY", ["по"])
        node.add(Node("Предлог", "по"))
        field = self.parse_field_name()
        if field == "количество":
            raise ParseError(
                message="Поле 'количество' нельзя использовать в GROUP BY.",
                token=self.current(),
                expected=["жанр", "режиссер", "год", "тип"],
            )
        self.spec.group_by = field
        node.add(Node("Поле", field))
        return node

    def parse_having_clause(self) -> Node:
        node = Node("Having")
        self.expect("HAVING", ["имея"])
        node.add(Node("Оператор", "имея"))
        field = self.parse_field_name()
        if field != "количество":
            raise ParseError(
                message="В HAVING поддерживается только 'количество'.",
                token=self.current(),
                expected=["количество"],
            )
        node.add(Node("Поле", field))
        op = self.parse_comparator()
        node.add(Node("Сравнение", op))
        num_tok = self.expect("NUMBER", ["число"])
        self.spec.having_operator = op
        self.spec.having_value = int(num_tok.value)
        node.add(Node("Значение", num_tok.value))
        return node

    def parse_order_by_clause(self) -> Node:
        node = Node("OrderBy")
        self.expect("ORDER", ["сортировать"])
        node.add(Node("Оператор", "сортировать"))
        self.expect("BY", ["по"])
        node.add(Node("Предлог", "по"))
        field = self.parse_field_name()
        self.spec.order_by = field
        node.add(Node("Поле", field))

        direction = "ASC"
        if self.current_type() in {"ASC", "DESC"}:
            dir_tok = self.advance()
            direction = "ASC" if dir_tok.token_type == "ASC" else "DESC"
            node.add(Node("Направление", dir_tok.value))
        self.spec.order_direction = direction
        return node

    def parse_comparator(self) -> str:
        tok = self.current()
        if tok is None:
            raise ParseError(
                message="Ожидался оператор сравнения.",
                token=None,
                expected=["больше", "меньше", "равно", "не равно"],
            )

        if tok.token_type == "CMP_SYMBOL":
            self.advance()
            return tok.value

        if tok.token_type == "GREATER":
            self.advance()
            if self.current_type() == "OR":
                self.advance()
                self.expect("EQUAL", ["равно"])
                return ">="
            return ">"

        if tok.token_type == "LESS":
            self.advance()
            if self.current_type() == "OR":
                self.advance()
                self.expect("EQUAL", ["равно"])
                return "<="
            return "<"

        if tok.token_type == "EQUAL":
            self.advance()
            return "="

        if tok.token_type == "NOT":
            self.advance()
            self.expect("EQUAL", ["равно"])
            return "!="

        raise ParseError(
            message="Некорректный оператор сравнения.",
            token=tok,
            expected=["больше", "меньше", "равно", "не равно"],
        )

    def parse_field_name(self) -> str:
        tok = self.current()
        if tok is None:
            raise ParseError(
                message="Ожидалось поле для SQL-клаузы.",
                token=None,
                expected=list(sorted(FIELD_WORDS)),
            )

        if tok.token_type == "FIELD":
            self.advance()
            return tok.value

        if tok.token_type == "YEAR_WORD":
            self.advance()
            return "год"

        raise ParseError(
            message="Ожидалось имя поля.",
            token=tok,
            expected=list(sorted(FIELD_WORDS)),
        )

    def parse_genre_filter(self) -> Node:
        node = Node("ФильтрЖанра")
        self.expect("BY", ["по"])
        node.add(Node("Предлог", "по"))
        genres = self.parse_genre_list()
        node.add(genres)
        return node

    def parse_director_filter(self) -> Node:
        node = Node("ФильтрРежиссера")
        directors = self.parse_director_list()
        node.add(directors)
        return node

    def parse_year_filter(self) -> Node:
        tok = self.current()
        if tok is None:
            raise ParseError(
                message="Ожидался фильтр по году, но запрос закончился.",
                token=None,
                expected=["YEAR", "после", "до", "с"],
            )

        node = Node("ФильтрГода")

        if tok.token_type == "YEAR":
            year_tok = self.advance()
            self.spec.year_condition = YearCondition(kind="eq", year_from=int(year_tok.value))
            node.add(Node("Год", year_tok.value))
            self.expect("YEAR_WORD", ["год"])
            node.add(Node("Слово", "год"))
            return node

        if tok.token_type == "AFTER":
            self.advance()
            node.add(Node("Оператор", "после"))
            year_tok = self.expect("YEAR", ["YEAR"])
            self.spec.year_condition = YearCondition(kind="gt", year_from=int(year_tok.value))
            node.add(Node("Год", year_tok.value))
            return node

        if tok.token_type == "BEFORE":
            self.advance()
            node.add(Node("Оператор", "до"))
            year_tok = self.expect("YEAR", ["YEAR"])
            self.spec.year_condition = YearCondition(kind="lt", year_from=int(year_tok.value))
            node.add(Node("Год", year_tok.value))
            return node

        if tok.token_type == "FROM":
            self.advance()
            node.add(Node("Оператор", "с"))
            year_from = self.expect("YEAR", ["YEAR"])
            self.expect("BY", ["по"])
            year_to = self.expect("YEAR", ["YEAR"])
            self.spec.year_condition = YearCondition(
                kind="between",
                year_from=int(year_from.value),
                year_to=int(year_to.value),
            )
            node.add(Node("ГодОт", year_from.value))
            node.add(Node("Оператор", "по"))
            node.add(Node("ГодДо", year_to.value))
            return node

        raise ParseError(
            message="Некорректное начало фильтра по году.",
            token=tok,
            expected=["YEAR", "после", "до", "с"],
        )

    def parse_genre_list(self) -> Node:
        node = Node("СписокЖанров")
        first = self.expect("GENRE", list(sorted(GENRES)))
        self.spec.genres.append(first.value)
        node.add(Node("Жанр", first.value))

        while True:
            tok = self.current()
            if tok is None:
                break

            if tok.token_type == "COMMA":
                self.advance()
                node.add(Node("Разделитель", ","))
                genre_tok = self.expect("GENRE", ["жанр"])
                self.spec.genres.append(genre_tok.value)
                node.add(Node("Жанр", genre_tok.value))
                continue

            if tok.token_type == "AND":
                self.advance()
                node.add(Node("Союз", "и"))
                genre_tok = self.expect("GENRE", ["жанр"])
                self.spec.genres.append(genre_tok.value)
                node.add(Node("Жанр", genre_tok.value))
                break

            break

        return node

    def parse_director_list(self) -> Node:
        node = Node("СписокРежиссеров")
        first = self.expect("DIRECTOR", list(sorted(DIRECTORS)))
        self.spec.directors.append(first.value)
        node.add(Node("Режиссер", first.value))

        while True:
            tok = self.current()
            if tok is None:
                break

            if tok.token_type == "COMMA":
                self.advance()
                node.add(Node("Разделитель", ","))
                director_tok = self.expect("DIRECTOR", ["режиссер"])
                self.spec.directors.append(director_tok.value)
                node.add(Node("Режиссер", director_tok.value))
                continue

            if tok.token_type == "AND":
                self.advance()
                node.add(Node("Союз", "и"))
                director_tok = self.expect("DIRECTOR", ["режиссер"])
                self.spec.directors.append(director_tok.value)
                node.add(Node("Режиссер", director_tok.value))
                break

            break

        return node
