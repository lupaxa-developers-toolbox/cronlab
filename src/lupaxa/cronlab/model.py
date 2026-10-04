"""Immutable cron expression."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    values: frozenset[int]
    restricted: bool
    raw: str


@dataclass(frozen=True)
class CronExpression:
    raw: str
    fields: tuple[Field, Field, Field, Field, Field]
