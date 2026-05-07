from typing import List

from .constants import FIELD_TO_DB, OBJECT_TO_DB
from .models import QuerySpec, SQLQuery


def build_sql(spec: QuerySpec) -> SQLQuery:
    if spec.object_type is None:
        raise ValueError("Не указан объект запроса.")

    params: List[object] = []
    where_parts: List[str] = []

    where_parts.append("type = ?")
    params.append(OBJECT_TO_DB[spec.object_type])

    if spec.genres:
        placeholders = ", ".join("?" for _ in spec.genres)
        where_parts.append(f"genre IN ({placeholders})")
        params.extend(spec.genres)

    if spec.directors:
        placeholders = ", ".join("?" for _ in spec.directors)
        where_parts.append(f"director IN ({placeholders})")
        params.extend(spec.directors)

    if spec.year_condition is not None:
        yc = spec.year_condition
        if yc.kind == "eq":
            where_parts.append("release_year = ?")
            params.append(yc.year_from)
        elif yc.kind == "gt":
            where_parts.append("release_year > ?")
            params.append(yc.year_from)
        elif yc.kind == "lt":
            where_parts.append("release_year < ?")
            params.append(yc.year_from)
        elif yc.kind == "between":
            where_parts.append("release_year BETWEEN ? AND ?")
            params.extend([yc.year_from, yc.year_to])

    select_part = "SELECT *"
    group_by_part = ""
    having_part = ""
    order_by_part = ""

    if spec.group_by is not None:
        group_field = FIELD_TO_DB[spec.group_by]
        select_part = f"SELECT {group_field}, COUNT(*) AS total_count"
        group_by_part = f"GROUP BY {group_field}"

    if spec.having_operator is not None:
        if spec.group_by is None:
            raise ValueError("HAVING нельзя использовать без GROUP BY.")
        having_part = f"HAVING COUNT(*) {spec.having_operator} ?"
        params.append(spec.having_value)

    if spec.order_by is not None:
        order_field = FIELD_TO_DB[spec.order_by]
        if order_field == "total_count" and spec.group_by is None:
            raise ValueError("Сортировка по количеству доступна только с GROUP BY.")
        direction = spec.order_direction or "ASC"
        order_by_part = f"ORDER BY {order_field} {direction}"

    sql_parts = [select_part, "FROM films"]
    if where_parts:
        sql_parts.append("WHERE " + " AND ".join(where_parts))
    if group_by_part:
        sql_parts.append(group_by_part)
    if having_part:
        sql_parts.append(having_part)
    if order_by_part:
        sql_parts.append(order_by_part)

    return SQLQuery(query=" ".join(sql_parts) + ";", params=params)
