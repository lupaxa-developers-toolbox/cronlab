"""Next-run search for a parsed cron expression."""

from __future__ import annotations

from calendar import monthrange
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lupaxa.cronlab.errors import HorizonError, TimezoneError
from lupaxa.cronlab.model import CronExpression

_MAX_ITERATIONS = 1_200_000
_HORIZON_DAYS = 730


def next_runs(
    expression: CronExpression,
    *,
    start: datetime,
    tz_name: str,
    count: int,
) -> list[datetime]:
    try:
        zone = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError) as exc:
        raise TimezoneError(f"unknown timezone: {tz_name}") from exc
    if start.tzinfo is None:
        raise TimezoneError("start must be timezone-aware")
    cursor = start.astimezone(zone)
    if cursor.second or cursor.microsecond:
        cursor = cursor.replace(second=0, microsecond=0) + timedelta(minutes=1)
    else:
        cursor = cursor + timedelta(minutes=1)
    horizon = start.astimezone(timezone.utc) + timedelta(days=_HORIZON_DAYS)
    found: list[datetime] = []
    iterations = 0
    while len(found) < count and iterations < _MAX_ITERATIONS:
        iterations += 1
        if cursor.astimezone(timezone.utc) > horizon:
            break
        matched = _localize_if_real(
            zone, cursor.year, cursor.month, cursor.day, cursor.hour, cursor.minute
        )
        if matched is not None and _matches(expression, matched):
            found.append(matched)
        cursor = cursor + timedelta(minutes=1)
    if not found:
        raise HorizonError("no runs within horizon")
    return found


def _localize_if_real(
    zone: ZoneInfo, year: int, month: int, day: int, hour: int, minute: int
) -> datetime | None:
    if day > monthrange(year, month)[1]:
        return None
    candidate = datetime(year, month, day, hour, minute, tzinfo=zone, fold=0)
    back = candidate.astimezone(timezone.utc).astimezone(zone)
    if (back.year, back.month, back.day, back.hour, back.minute) != (
        year,
        month,
        day,
        hour,
        minute,
    ):
        return None
    return candidate.replace(fold=0)


def _matches(expression: CronExpression, instant: datetime) -> bool:
    minute, hour, dom, month, dow = expression.fields
    if instant.minute not in minute.values:
        return False
    if instant.hour not in hour.values:
        return False
    if instant.month not in month.values:
        return False
    cron_dow = instant.isoweekday() % 7
    dow_ok = cron_dow in dow.values or (cron_dow == 0 and 7 in dow.values)
    dom_ok = instant.day in dom.values
    if dom.restricted and dow.restricted:
        return dom_ok or dow_ok
    if dom.restricted:
        return dom_ok
    if dow.restricted:
        return dow_ok
    return True
