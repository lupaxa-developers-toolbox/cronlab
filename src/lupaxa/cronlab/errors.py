"""Errors for lupaxa.cronlab."""

from __future__ import annotations


class CronlabError(Exception):
    """Base error."""


class ParseError(CronlabError):
    """Wrong field count, bad token, or unsupported syntax."""


class ValidationError(CronlabError):
    """Out of range or empty allowed set."""


class TimezoneError(CronlabError):
    """Unknown IANA timezone name."""


class FromError(CronlabError):
    """Unreadable or naive --from instant."""


class HorizonError(CronlabError):
    """No match inside the two-year search window."""
