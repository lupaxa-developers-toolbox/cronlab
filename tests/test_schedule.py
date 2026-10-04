"""Next-run calculations."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from lupaxa.cronlab.errors import HorizonError, TimezoneError
from lupaxa.cronlab.parse import parse
from lupaxa.cronlab.schedule import next_runs


def test_exclusive_daily_nine() -> None:
    expr = parse("0 9 * * *")
    start = datetime(2026, 10, 4, 9, 0, tzinfo=timezone.utc)
    runs = next_runs(expr, start=start, tz_name="UTC", count=1)
    assert runs == [datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc)]


def test_leap_day_2024_not_2025() -> None:
    expr = parse("0 0 29 2 *")
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    runs = next_runs(expr, start=start, tz_name="UTC", count=1)
    assert runs == [datetime(2024, 2, 29, 0, 0, tzinfo=timezone.utc)]
    start_2025 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(HorizonError, match="horizon"):
        next_runs(expr, start=start_2025, tz_name="UTC", count=1)


def test_april_31_never_matches() -> None:
    expr = parse("0 0 31 4 *")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(HorizonError, match="horizon"):
        next_runs(expr, start=start, tz_name="UTC", count=1)


def test_day_field_or() -> None:
    expr = parse("0 0 1 * 1")
    start = datetime(2026, 5, 31, tzinfo=timezone.utc)
    runs = next_runs(expr, start=start, tz_name="UTC", count=3)
    assert datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc) in runs
    mondays = [item for item in runs if item.isoweekday() == 1]
    assert mondays


def test_unknown_timezone() -> None:
    expr = parse("* * * * *")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(TimezoneError):
        next_runs(expr, start=start, tz_name="Not/AZone", count=1)


def test_london_spring_gap_skips_0130() -> None:
    expr = parse("30 1 * * *")
    start = datetime(2026, 3, 28, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(expr, start=start, tz_name="Europe/London", count=3)
    walls = [(item.year, item.month, item.day, item.hour, item.minute) for item in runs]
    assert (2026, 3, 29, 1, 30) not in walls
    assert (2026, 3, 28, 1, 30) in walls
    assert (2026, 3, 30, 1, 30) in walls


def test_london_autumn_fold_once() -> None:
    expr = parse("30 1 * * *")
    start = datetime(2026, 10, 24, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(expr, start=start, tz_name="Europe/London", count=2)
    first = [item for item in runs if item.date().isoformat() == "2026-10-25"]
    assert len(first) == 1
    assert first[0].fold == 0
    offset = first[0].utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 3600
