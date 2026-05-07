import re
from typing import List, Tuple

from .constants import (
    AFTER,
    ASC_WORDS,
    BEFORE,
    COMMANDS,
    CONJUNCTION,
    DESC_WORDS,
    DIRECTORS,
    DSL_VOCABULARY,
    EQUAL_WORD,
    FIELD_WORDS,
    FROM,
    GENRES,
    GREATER_WORD,
    GROUP_WORD,
    HAVING_WORD,
    LESS_WORD,
    MORPH,
    NOT_WORD,
    OBJECTS,
    OR_WORD,
    ORDER_WORD,
    PREP_BY,
    QUANTIFIERS,
    SPECIAL_NORMAL_FORMS,
    YEAR_WORD,
)
from .models import RawToken, Token


def tokenize(text: str) -> List[RawToken]:
    pattern = r"\d+|[А-Яа-яЁё-]+|,|>=|<=|!=|=|>|<"
    parts = re.findall(pattern, text)
    return [RawToken(text=part, index=i) for i, part in enumerate(parts)]


def normalize_word(word: str) -> str:
    lower_word = word.lower()
    if lower_word in SPECIAL_NORMAL_FORMS:
        return SPECIAL_NORMAL_FORMS[lower_word]

    if lower_word in DSL_VOCABULARY:
        return lower_word

    if MORPH is None:
        return lower_word

    lemma = MORPH.parse(lower_word)[0].normal_form
    if lemma == "режиссёр":
        lemma = "режиссер"
    return lemma


def normalize_raw_tokens(raw_tokens: List[RawToken]) -> List[str]:
    normalized = []
    for tok in raw_tokens:
        if tok.text in {",", ">=", "<=", "!=", "=", ">", "<"}:
            normalized.append(tok.text)
        elif re.fullmatch(r"\d+", tok.text):
            normalized.append(tok.text)
        else:
            normalized.append(normalize_word(tok.text))
    return normalized


def classify_token(raw_token: RawToken, normalized: str) -> Token:
    raw = raw_token.text

    if normalized == ",":
        return Token("COMMA", ",", raw, raw_token.index)
    if normalized in {">=", "<=", "!=", "=", ">", "<"}:
        return Token("CMP_SYMBOL", normalized, raw, raw_token.index)
    if re.fullmatch(r"\d{4}", normalized):
        return Token("YEAR", normalized, raw, raw_token.index)
    if re.fullmatch(r"\d+", normalized):
        return Token("NUMBER", normalized, raw, raw_token.index)
    if normalized in COMMANDS:
        return Token("COMMAND", normalized, raw, raw_token.index)
    if normalized in QUANTIFIERS:
        return Token("QUANTIFIER", normalized, raw, raw_token.index)
    if normalized in OBJECTS:
        return Token("OBJECT", normalized, raw, raw_token.index)
    if normalized in GENRES:
        return Token("GENRE", normalized, raw, raw_token.index)
    if normalized in DIRECTORS:
        return Token("DIRECTOR", normalized, raw, raw_token.index)
    if normalized == CONJUNCTION:
        return Token("AND", normalized, raw, raw_token.index)
    if normalized == OR_WORD:
        return Token("OR", normalized, raw, raw_token.index)
    if normalized == PREP_BY:
        return Token("BY", normalized, raw, raw_token.index)
    if normalized == AFTER:
        return Token("AFTER", normalized, raw, raw_token.index)
    if normalized == BEFORE:
        return Token("BEFORE", normalized, raw, raw_token.index)
    if normalized == FROM:
        return Token("FROM", normalized, raw, raw_token.index)
    if normalized == YEAR_WORD:
        return Token("YEAR_WORD", normalized, raw, raw_token.index)
    if normalized in FIELD_WORDS:
        return Token("FIELD", normalized, raw, raw_token.index)
    if normalized == GROUP_WORD:
        return Token("GROUP", normalized, raw, raw_token.index)
    if normalized == HAVING_WORD:
        return Token("HAVING", normalized, raw, raw_token.index)
    if normalized == ORDER_WORD:
        return Token("ORDER", normalized, raw, raw_token.index)
    if normalized == GREATER_WORD:
        return Token("GREATER", normalized, raw, raw_token.index)
    if normalized == LESS_WORD:
        return Token("LESS", normalized, raw, raw_token.index)
    if normalized == EQUAL_WORD:
        return Token("EQUAL", normalized, raw, raw_token.index)
    if normalized == NOT_WORD:
        return Token("NOT", normalized, raw, raw_token.index)
    if normalized in ASC_WORDS:
        return Token("ASC", normalized, raw, raw_token.index)
    if normalized in DESC_WORDS:
        return Token("DESC", normalized, raw, raw_token.index)

    return Token("UNKNOWN", normalized, raw, raw_token.index)


def lex_query(query: str) -> Tuple[List[RawToken], List[str], List[Token]]:
    raw_tokens = tokenize(query)
    normalized = normalize_raw_tokens(raw_tokens)
    tokens = [classify_token(rt, norm) for rt, norm in zip(raw_tokens, normalized)]
    return raw_tokens, normalized, tokens


def normalized_query_string(normalized_tokens: List[str]) -> str:
    return " ".join(normalized_tokens)
