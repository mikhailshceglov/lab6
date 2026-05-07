from dsl_sql.service import analyze_query, print_analysis


query = "найди фильмы по драме"   # измените на свой запрос


result = analyze_query(query)
print_analysis(result)
