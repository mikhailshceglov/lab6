from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RawToken:
    text: str
    index: int


@dataclass
class Token:
    token_type: str
    value: str
    raw_text: str
    index: int


@dataclass
class Node:
    name: str
    value: Optional[str] = None
    children: List["Node"] = field(default_factory=list)

    def add(self, child: "Node") -> None:
        self.children.append(child)


@dataclass
class YearCondition:
    kind: str
    year_from: int
    year_to: Optional[int] = None


@dataclass
class QuerySpec:
    object_type: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    directors: List[str] = field(default_factory=list)
    year_condition: Optional[YearCondition] = None
    group_by: Optional[str] = None
    having_operator: Optional[str] = None
    having_value: Optional[int] = None
    order_by: Optional[str] = None
    order_direction: Optional[str] = None


@dataclass
class SQLQuery:
    query: str
    params: List[object]


class ParseError(Exception):
    def __init__(self, message: str, token: Optional[Token], expected: Optional[List[str]] = None):
        self.message = message
        self.token = token
        self.expected = expected or []
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.token is None:
            where = "в конце запроса"
            got = "EOF"
            pos = "-"
        else:
            where = f"на токене #{self.token.index + 1}"
            got = f"'{self.token.raw_text}'"
            pos = str(self.token.index + 1)

        expected_part = ""
        if self.expected:
            expected_part = f"\nОжидалось: {', '.join(self.expected)}"

        return (
            f"Ошибка синтаксического анализа {where}.\n"
            f"Позиция: {pos}\n"
            f"Получено: {got}\n"
            f"Сообщение: {self.message}"
            f"{expected_part}"
        )
