from dsl_sql.service import analyze_query


def test_basic_query_to_sql():
    result = analyze_query("найди все фильмы")
    assert result["success"] is True
    assert result["sql"] == "SELECT * FROM films WHERE type = ?;"
    assert result["sql_params"] == ["film"]


def test_year_range_query_to_sql():
    result = analyze_query("найди фильмы с 2010 по 2020")
    assert result["success"] is True
    assert result["sql"] == "SELECT * FROM films WHERE type = ? AND release_year BETWEEN ? AND ?;"
    assert result["sql_params"] == ["film", 2010, 2020]


def test_genre_and_director_filters():
    result = analyze_query("найди фильмы Нолана и Тарантино")
    assert result["success"] is True
    assert "director IN (?, ?)" in result["sql"]
    assert result["sql_params"] == ["film", "нолан", "тарантино"]


def test_group_having_order_query():
    query = "найди фильмы по драме группировать по жанр имея количество >= 1 сортировать по количество убыванию"
    result = analyze_query(query)
    assert result["success"] is True
    assert "GROUP BY genre" in result["sql"]
    assert "HAVING COUNT(*) >= ?" in result["sql"]
    assert "ORDER BY total_count DESC" in result["sql"]
    assert result["sql_params"] == ["film", "драма", 1]


def test_lexical_error_returns_no_sql():
    result = analyze_query("найди фильмы авокадо")
    assert result["success"] is False
    assert "Лексическая ошибка" in result["error"]
    assert result["sql"] is None
    assert result["sql_params"] is None


def test_syntax_error_returns_no_sql():
    result = analyze_query("найди фильмы по , драме")
    assert result["success"] is False
    assert "Ошибка синтаксического анализа" in result["error"]
    assert result["sql"] is None
    assert result["sql_params"] is None
