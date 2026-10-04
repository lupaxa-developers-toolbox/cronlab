"""Parse a five-field Vixie cron expression."""

from __future__ import annotations

import re

from lupaxa.cronlab.errors import ParseError
from lupaxa.cronlab.model import CronExpression, Field
from lupaxa.cronlab.validate import validate

_FIELD_SPECS: tuple[tuple[str, int, int], ...] = (
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day_of_month", 1, 31),
    ("month", 1, 12),
    ("day_of_week", 0, 7),
)

_UNSUPPORTED = re.compile(r"(?i)(?:@[a-z]+|[a-z]+|[LW#?])")


def parse(expression: str) -> CronExpression:
    text = expression.strip()
    if text.startswith("@"):
        raise ParseError(f"unsupported macro: {text}")
    parts = text.split()
    if len(parts) != 5:
        raise ParseError(f"expected 5 fields, got {len(parts)}")
    minute, hour, day_of_month, month, day_of_week = (
        _parse_field(name, raw, low, high)
        for (name, low, high), raw in zip(_FIELD_SPECS, parts, strict=True)
    )
    result = CronExpression(
        raw=text,
        fields=(minute, hour, day_of_month, month, day_of_week),
    )
    validate(result)
    return result


def _parse_field(name: str, raw: str, low: int, high: int) -> Field:
    if _UNSUPPORTED.search(raw):
        raise ParseError(f"unsupported syntax in {name}: {raw}")
    if raw == "*":
        return Field(name, frozenset(range(low, high + 1)), False, raw)
    values: set[int] = set()
    for chunk in raw.split(","):
        values.update(_parse_chunk(name, chunk, low, high))
    return Field(name, frozenset(values), True, raw)


def _parse_chunk(name: str, chunk: str, low: int, high: int) -> set[int]:
    if not chunk:
        raise ParseError(f"empty term in {name}")
    if "/" in chunk:
        body, step_text = chunk.split("/", 1)
        if not step_text.isdigit() or int(step_text) < 1:
            raise ParseError(f"invalid step in {name}: {chunk}")
        step = int(step_text)
        if body == "*":
            return set(range(low, high + 1, step))
        if "-" in body:
            start, end = _parse_range(name, body, chunk)
            return set(range(start, end + 1, step))
        raise ParseError(f"unsupported stepped form in {name}: {chunk}")
    if "-" in chunk:
        start, end = _parse_range(name, chunk, chunk)
        return set(range(start, end + 1))
    if chunk.isdigit():
        return {int(chunk)}
    raise ParseError(f"invalid term in {name}: {chunk}")


def _parse_range(name: str, body: str, chunk: str) -> tuple[int, int]:
    left, right = body.split("-", 1)
    if not left.isdigit() or not right.isdigit():
        raise ParseError(f"invalid range in {name}: {chunk}")
    start, end = int(left), int(right)
    if start > end:
        raise ParseError(f"inverted range in {name}: {chunk}")
    return start, end
