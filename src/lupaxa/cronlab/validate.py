"""Range and emptiness checks."""

from __future__ import annotations

from lupaxa.cronlab.errors import ValidationError
from lupaxa.cronlab.model import CronExpression

_BOUNDS = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}


def validate(expression: CronExpression) -> None:
    for field in expression.fields:
        low, high = _BOUNDS[field.name]
        if not field.values:
            raise ValidationError(f"{field.name} has no allowed values")
        if any(value < low or value > high for value in field.values):
            raise ValidationError(f"{field.name} value out of range {low}-{high}")
