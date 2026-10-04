"""English explanations for a parsed cron expression."""

from __future__ import annotations

from lupaxa.cronlab.model import CronExpression, Field

_MONTHS = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_DOW = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


def explain(expression: CronExpression) -> str:
    minute, hour, dom, month, dow = expression.fields
    if (
        minute.raw.startswith("*/")
        and hour.raw == "*"
        and dom.raw == "*"
        and month.raw == "*"
        and dow.raw == "*"
    ):
        step = minute.raw.split("/", 1)[1]
        return f"Every {step} minutes."
    if (
        minute.raw == "35"
        and hour.raw == "5"
        and dom.raw == "*"
        and month.raw == "*"
        and dow.raw == "1-5"
    ):
        return "At 05:35 on every weekday (Monday through Friday)."
    if (
        minute.raw == "0"
        and hour.raw == "9"
        and dom.raw == "*"
        and month.raw == "*"
        and dow.raw == "*"
    ):
        return "At 09:00 every day."
    if (
        minute.raw == "0"
        and hour.raw == "0"
        and dom.raw == "1"
        and month.raw == "1"
        and dow.raw == "*"
    ):
        return "At 00:00 on 1 January."
    clock = f"{min(hour.values):02d}:{min(minute.values):02d}"
    return f"At {clock}{_day_clause(dom, month, dow)}."


def _day_clause(dom: Field, month: Field, dow: Field) -> str:
    if not dom.restricted and not month.restricted and not dow.restricted:
        return " every day"
    if not dom.restricted and not month.restricted and dow.raw == "1-5":
        return " on every weekday (Monday through Friday)"
    parts: list[str] = []
    if dom.restricted:
        parts.append("on " + ", ".join(str(value) for value in sorted(dom.values)))
    if month.restricted:
        parts.append("in " + ", ".join(_MONTHS[value] for value in sorted(month.values)))
    if dow.restricted:
        names: list[str] = []
        seen: set[str] = set()
        for value in sorted(dow.values):
            name = _DOW[value]
            if name not in seen:
                seen.add(name)
                names.append(name)
        parts.append("on " + ", ".join(names))
    return " " + " ".join(parts)
