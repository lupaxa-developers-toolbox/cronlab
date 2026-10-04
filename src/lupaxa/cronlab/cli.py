"""Command-line interface for lupaxa.cronlab."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any

from lupaxa.cronlab import __version__
from lupaxa.cronlab.errors import (
    CronlabError,
    FromError,
    HorizonError,
    ParseError,
    TimezoneError,
    ValidationError,
)
from lupaxa.cronlab.explain import explain
from lupaxa.cronlab.parse import parse
from lupaxa.cronlab.schedule import next_runs

_EXIT_USAGE = 2
_EXIT_HORIZON = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate, explain, and preview five-field Vixie cron expressions."
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit.",
    )
    sub = parser.add_subparsers(dest="command")

    validate_cmd = sub.add_parser("validate", help="Check that an expression is valid.")
    validate_cmd.add_argument("expression")
    validate_cmd.add_argument("--json", action="store_true")

    explain_cmd = sub.add_parser("explain", help="Describe an expression in English.")
    explain_cmd.add_argument("expression")
    explain_cmd.add_argument("--json", action="store_true")

    next_cmd = sub.add_parser("next", help="Preview future run times.")
    next_cmd.add_argument("expression")
    next_cmd.add_argument("--timezone", default="UTC")
    next_cmd.add_argument("--from", dest="from_text", default=None)
    next_cmd.add_argument("--count", type=int, default=5)
    next_cmd.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"cronlab {__version__}")
        return 0

    if not args.command:
        print("error: a command is required", file=sys.stderr)
        return 2

    if args.command == "next" and (args.count < 1 or args.count > 100):
        print("error: --count must be between 1 and 100", file=sys.stderr)
        return 2

    as_json = bool(getattr(args, "json", False))
    try:
        return _run(args, as_json)
    except (ParseError, ValidationError, TimezoneError, FromError) as exc:
        return _fail(exc, args, as_json, _EXIT_USAGE)
    except HorizonError as exc:
        return _fail(exc, args, as_json, _EXIT_HORIZON)
    except CronlabError as exc:
        return _fail(exc, args, as_json, _EXIT_HORIZON)


def _run(args: argparse.Namespace, as_json: bool) -> int:
    expression = parse(args.expression)
    if args.command == "validate":
        if as_json:
            print(json.dumps(_envelope(args, ok=True)))
        else:
            print("valid")
        return 0
    if args.command == "explain":
        text = explain(expression)
        if as_json:
            payload = _envelope(args, ok=True)
            payload["explanation"] = text
            print(json.dumps(payload))
        else:
            print(text)
        return 0
    start = _parse_from(args.from_text) if args.from_text else datetime.now(timezone.utc)
    runs = next_runs(expression, start=start, tz_name=args.timezone, count=args.count)
    formatted = [item.isoformat(timespec="seconds") for item in runs]
    if as_json:
        payload = _envelope(args, ok=True, start=start)
        payload["runs"] = formatted
        payload["count"] = args.count
        print(json.dumps(payload))
    else:
        print("\n".join(formatted))
    return 0


def _parse_from(text: str) -> datetime:
    raw = text.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        instant = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise FromError(f"unreadable --from: {text}") from exc
    if instant.tzinfo is None:
        raise FromError("naive --from is not allowed")
    return instant


def _envelope(
    args: argparse.Namespace,
    *,
    ok: bool,
    start: datetime | None = None,
    error: CronlabError | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "dialect": "vixie",
        "expression": getattr(args, "expression", None),
        "command": args.command,
        "timezone": args.timezone if args.command == "next" else "UTC",
        "from": start.isoformat(timespec="seconds") if start is not None else None,
        "inclusive": False,
        "dst_policy": "skip_gap_first_fold",
        "horizon": {"years": 2},
        "ok": ok,
    }
    if error is not None:
        payload["error"] = {"type": type(error).__name__, "message": str(error)}
    return payload


def _fail(exc: CronlabError, args: argparse.Namespace, as_json: bool, code: int) -> int:
    if as_json:
        print(json.dumps(_envelope(args, ok=False, error=exc)))
    else:
        print(f"error: {exc}", file=sys.stderr)
    return code
