"""CLI contract."""

from __future__ import annotations

import json

from lupaxa.cronlab.cli import main


def test_version(capsys) -> None:
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.startswith("cronlab ")


def test_validate_ok(capsys) -> None:
    assert main(["validate", "35 5 * * 1-5"]) == 0
    assert capsys.readouterr().out.strip() == "valid"


def test_validate_bad(capsys) -> None:
    assert main(["validate", "@daily"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("error: ")


def test_explain(capsys) -> None:
    assert main(["explain", "0 9 * * *"]) == 0
    assert capsys.readouterr().out.strip() == "At 09:00 every day."


def test_next_human(capsys) -> None:
    code = main(
        [
            "next",
            "0 9 * * *",
            "--from",
            "2026-10-04T09:00:00+00:00",
            "--timezone",
            "UTC",
            "--count",
            "1",
        ]
    )
    assert code == 0
    assert capsys.readouterr().out.strip() == "2026-10-05T09:00:00+00:00"


def test_next_horizon(capsys) -> None:
    code = main(["next", "0 0 31 2 *", "--from", "2026-01-01T00:00:00Z", "--count", "1"])
    assert code == 1
    assert "horizon" in capsys.readouterr().err


def test_json_validate(capsys) -> None:
    assert main(["validate", "0 9 * * *", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dialect"] == "vixie"
    assert payload["command"] == "validate"
    assert payload["timezone"] == "UTC"
    assert payload["from"] is None
    assert payload["inclusive"] is False
    assert payload["dst_policy"] == "skip_gap_first_fold"
    assert payload["horizon"] == {"years": 2}


def test_json_next(capsys) -> None:
    code = main(
        [
            "next",
            "0 9 * * *",
            "--from",
            "2026-10-04T09:00:00Z",
            "--json",
            "--count",
            "1",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["runs"] == ["2026-10-05T09:00:00+00:00"]
    assert payload["count"] == 1
    assert payload["from"].endswith("+00:00")


def test_naive_from(capsys) -> None:
    code = main(["next", "0 9 * * *", "--from", "2026-10-04T09:00:00"])
    assert code == 2
    assert capsys.readouterr().err.startswith("error: ")


def test_count_out_of_range() -> None:
    assert main(["next", "* * * * *", "--count", "0"]) == 2
