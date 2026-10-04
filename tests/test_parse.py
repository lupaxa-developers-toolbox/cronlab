"""Vixie field grammar and validation."""

from __future__ import annotations

import pytest

from lupaxa.cronlab.errors import ParseError, ValidationError
from lupaxa.cronlab.parse import parse


def test_wildcard_is_unrestricted() -> None:
    expr = parse("* * * * *")
    assert expr.fields[0].restricted is False
    assert expr.fields[0].values == frozenset(range(0, 60))


def test_list_range_and_step() -> None:
    expr = parse("1,15,30-40/2 * * * *")
    assert 1 in expr.fields[0].values
    assert 15 in expr.fields[0].values
    assert 30 in expr.fields[0].values
    assert 32 in expr.fields[0].values
    assert 31 not in expr.fields[0].values
    assert expr.fields[0].restricted is True


def test_star_step_minutes() -> None:
    expr = parse("*/15 * * * *")
    assert expr.fields[0].values == frozenset({0, 15, 30, 45})
    assert expr.fields[0].restricted is True


def test_sunday_zero_and_seven() -> None:
    zero = parse("0 0 * * 0")
    seven = parse("0 0 * * 7")
    assert 0 in zero.fields[4].values
    assert 7 in seven.fields[4].values


def test_both_day_fields_restricted() -> None:
    expr = parse("0 0 1 * 1")
    assert expr.fields[2].restricted is True
    assert expr.fields[4].restricted is True


def test_inverted_range_is_parse_error() -> None:
    with pytest.raises(ParseError, match="range"):
        parse("10-1 * * * *")


def test_zero_step_is_parse_error() -> None:
    with pytest.raises(ParseError, match="step"):
        parse("*/0 * * * *")


def test_lone_integer_step_is_parse_error() -> None:
    with pytest.raises(ParseError, match="unsupported|step"):
        parse("5/2 * * * *")


def test_six_fields_is_parse_error() -> None:
    with pytest.raises(ParseError, match="field"):
        parse("0 0 * * * *")


def test_macro_is_parse_error() -> None:
    with pytest.raises(ParseError, match="macro|@|unsupported"):
        parse("@daily")


def test_named_month_is_parse_error() -> None:
    with pytest.raises(ParseError, match="unsupported|name|JAN"):
        parse("0 0 * JAN *")


def test_l_syntax_is_parse_error() -> None:
    with pytest.raises(ParseError, match="unsupported|L"):
        parse("0 0 L * *")


def test_out_of_range_is_validation_error() -> None:
    with pytest.raises(ValidationError, match="minute|range|60"):
        parse("60 * * * *")
