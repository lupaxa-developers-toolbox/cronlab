"""Human-readable Vixie explanations."""

from __future__ import annotations

from lupaxa.cronlab.explain import explain
from lupaxa.cronlab.parse import parse


def test_weekdays_at_0535() -> None:
    assert explain(parse("35 5 * * 1-5")) == ("At 05:35 on every weekday (Monday through Friday).")


def test_every_day_at_0900() -> None:
    assert explain(parse("0 9 * * *")) == "At 09:00 every day."


def test_every_15_minutes() -> None:
    assert explain(parse("*/15 * * * *")) == "Every 15 minutes."


def test_new_year() -> None:
    assert explain(parse("0 0 1 1 *")) == "At 00:00 on 1 January."
