from typing import Dict, List

from .lexer import lex_query, normalized_query_string
from .models import ParseError
from .parser import Parser
from .translator import build_sql
from .tree import tree_to_text


def analyze_query(query: str) -> Dict[str, object]:
    raw_tokens, normalized_tokens, tokens = lex_query(query)

    unknown_tokens = [tok for tok in tokens if tok.token_type == "UNKNOWN"]
    if unknown_tokens:
        bad = unknown_tokens[0]
        return {
            "query": query,
            "normalized_query": normalized_query_string(normalized_tokens),
            "success": False,
            "error": (
                f"Лексическая ошибка на токене #{bad.index + 1}: '{bad.raw_text}'.\n"
                f"Неизвестная лексема после лемматизации: '{bad.value}'."
            ),
            "tree": None,
            "sql": None,
            "sql_params": None,
            "tokens": tokens,
            "spec": None,
        }

    try:
        parser = Parser(tokens)
        tree, spec = parser.parse()
        sql_obj = build_sql(spec)
        return {
            "query": query,
            "normalized_query": normalized_query_string(normalized_tokens),
            "success": True,
            "error": None,
            "tree": tree_to_text(tree),
            "sql": sql_obj.query,
            "sql_params": sql_obj.params,
            "tokens": tokens,
            "spec": spec,
        }
    except (ParseError, ValueError) as exc:
        return {
            "query": query,
            "normalized_query": normalized_query_string(normalized_tokens),
            "success": False,
            "error": str(exc),
            "tree": None,
            "sql": None,
            "sql_params": None,
            "tokens": tokens,
            "spec": None,
        }


def analyze_queries(queries: List[str]) -> List[Dict[str, object]]:
    return [analyze_query(q) for q in queries if q.strip()]


def print_analysis(result: Dict[str, object]) -> None:
    print("=" * 69)
    print(f"Исходный запрос: {result['query']}")
    print(f"Нормализованный запрос: {result['normalized_query']}")
    print(f"Результат: {'УСПЕХ' if result['success'] else 'ОШИБКА'}")
    if result["success"]:
        print("Дерево разбора:")
        print(result["tree"])
        print("SQL:")
        print(result["sql"])
        print(f"Параметры: {result['sql_params']}")
    else:
        print("Диагностика:")
        print(result["error"])


def print_analysis_batch(results: List[Dict[str, object]]) -> None:
    for result in results:
        print_analysis(result)


def read_queries_from_file(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]
