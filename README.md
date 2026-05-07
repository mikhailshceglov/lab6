# DSL → SQL парсер

Парсер, преобразующий текстовые запросы на русском языке в SQL-запросы для базы данных фильмов.

## Описание

Проект реализует предметно-ориентированный язык (DSL) для поиска фильмов, сериалов и мультфильмов. Поддерживает фильтрацию по жанру, режиссёру, году выпуска, а также SQL-конструкции GROUP BY, HAVING и ORDER BY.

## Использование

```python
from dsl_sql import analyze_query

result = analyze_query("найди фильмы по драме")
print(result["sql"])  # SELECT * FROM films WHERE type = ? AND genre IN (?);
```

## Примеры

| Запрос | SQL |
|--------|-----|
| `найди все фильмы` | `SELECT * FROM films WHERE type = ?;` |
| `покажи сериалы 2020 года` | `SELECT * FROM films WHERE type = ? AND release_year = ?;` |
| `найди фильмы Нолана` | `SELECT * FROM films WHERE type = ? AND director IN (?);` |
| `найди фильмы по драме, комедии` | `SELECT * FROM films WHERE type = ? AND genre IN (?, ?);` |
| `найди фильмы после 2015` | `SELECT * FROM films WHERE type = ? AND release_year > ?;` |
| `найди фильмы с 2010 по 2020` | `SELECT * FROM films WHERE type = ? AND release_year BETWEEN ? AND ?;` |
| `найди фильмы по драме группировать по жанр` | `SELECT genre, COUNT(*) AS total_count FROM films WHERE type = ? AND genre IN (?) GROUP BY genre;` |
| `найди фильмы по драме группировать по жанр имея количество > 1` | `SELECT genre, COUNT(*) AS total_count FROM films WHERE type = ? AND genre IN (?) GROUP BY genre HAVING COUNT(*) > ?;` |
| `найди фильмы сортировать по год убыванию` | `SELECT * FROM films WHERE type = ? ORDER BY release_year DESC;` |

## Запуск

```bash
source .venv/bin/activate
pytest
python run_one.py
```
