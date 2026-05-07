try:
    import pymorphy3
except ImportError:  # pragma: no cover
    pymorphy3 = None

COMMANDS = {"найти", "показать", "вывести"}
QUANTIFIERS = {"весь", "всё"}
OBJECTS = {"фильм", "сериал", "мультфильм"}
GENRES = {"драма", "комедия", "триллер", "фантастика", "боевик", "детектив"}
DIRECTORS = {"нолан", "тарантино", "спилберг", "скорсезе", "миядзаки"}

CONJUNCTION = "и"
OR_WORD = "или"
PREP_BY = "по"
AFTER = "после"
BEFORE = "до"
FROM = "с"
YEAR_WORD = "год"

GROUP_WORD = "группировать"
HAVING_WORD = "имея"
ORDER_WORD = "сортировать"

FIELD_WORDS = {"жанр", "режиссер", "год", "тип", "количество"}

GREATER_WORD = "больше"
LESS_WORD = "меньше"
EQUAL_WORD = "равно"
NOT_WORD = "не"

ASC_WORDS = {"возрастание", "возрастанию"}
DESC_WORDS = {"убывание", "убыванию"}

OBJECT_TO_DB = {
    "фильм": "film",
    "сериал": "series",
    "мультфильм": "animation",
}

FIELD_TO_DB = {
    "жанр": "genre",
    "режиссер": "director",
    "год": "release_year",
    "тип": "type",
    "количество": "total_count",
}

SPECIAL_NORMAL_FORMS = {
    "все": "весь",
    "всё": "весь",
    "найди": "найти",
    "покажи": "показать",
    "выведи": "вывести",
    "режиссёр": "режиссер",
    "года": "год",
    "фильмы": "фильм",
    "фильма": "фильм",
    "сериалы": "сериал",
    "сериала": "сериал",
    "мультфильмы": "мультфильм",
    "мультфильма": "мультфильм",
    "драме": "драма",
    "драмы": "драма",
    "комедии": "комедия",
    "триллеру": "триллер",
    "триллера": "триллер",
    "фантастике": "фантастика",
    "боевике": "боевик",
    "детективе": "детектив",
    "нолана": "нолан",
    "тарантино": "тарантино",
    "спилберга": "спилберг",
    "скорсезе": "скорсезе",
    "миядзаки": "миядзаки",
}

DSL_VOCABULARY = (
    COMMANDS
    | QUANTIFIERS
    | OBJECTS
    | GENRES
    | DIRECTORS
    | FIELD_WORDS
    | {
        CONJUNCTION,
        OR_WORD,
        PREP_BY,
        AFTER,
        BEFORE,
        FROM,
        YEAR_WORD,
        GROUP_WORD,
        HAVING_WORD,
        ORDER_WORD,
        GREATER_WORD,
        LESS_WORD,
        EQUAL_WORD,
        NOT_WORD,
    }
    | ASC_WORDS
    | DESC_WORDS
)

MORPH = pymorphy3.MorphAnalyzer() if pymorphy3 is not None else None
