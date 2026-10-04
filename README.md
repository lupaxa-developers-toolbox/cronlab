<p align="center">
  <a href="https://github.com/lupaxa-developers-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/developers-toolbox/readme-logo.png" alt="Developers Toolbox" />
  </a>
</p>

<h1 align="center">Cronlab</h1>

Validate, explain, and preview five-field Vixie cron expressions.
The playground does not run jobs.

The PyPI name is `lupaxa-cronlab`. The import path is `lupaxa.cronlab`.
The console script is `cronlab`. `lupaxa` is a namespace package — there
is no `lupaxa/__init__.py`.

## Install

```bash
pip install lupaxa-cronlab
```

Requires Python 3.10+. There are no runtime dependencies.

> **Note:** On platforms without OS timezone data, install the `tzdata` package so IANA names resolve.

## What it Does

`cronlab` speaks one dialect: Vixie crontab, the same five-field shape
used by Linux `crontab(5)` and GitHub Actions `on.schedule`. Quote the
expression in the shell.

```bash
cronlab validate '35 5 * * 1-5'
cronlab explain '35 5 * * 1-5'
cronlab next '35 5 * * 1-5' --timezone Europe/London --from '2026-10-04T00:00:00+01:00' --count 5
cronlab next '0 9 * * *' --from '2026-10-04T00:00:00+01:00'
cronlab --version
```

| Flag          | Commands  | Default         | Meaning                            |
| ------------- | --------- | --------------- | ---------------------------------- |
| `--timezone`  | `next`    | `UTC`           | IANA zone for civil cron fields    |
| `--from`      | `next`    | now (UTC clock) | Exclusive start instant            |
| `--count`     | `next`    | `5`             | Number of future instants, 1–100   |
| `--json`      | all three | off             | Metadata envelope on stdout        |
| `--version`   | top-level | —               | Print `cronlab` and the version    |

## Validate

```bash
cronlab validate '35 5 * * 1-5'
```

```text
valid
```

Unsupported syntax is rejected. `@daily`, month names, and a sixth field
are not in this dialect.

```bash
cronlab validate '@daily'
```

```text
error: unsupported macro: @daily
```

```bash
cronlab validate '0 0 * JAN *'
```

```text
error: unsupported syntax in month: JAN
```

## Explain

```bash
cronlab explain '35 5 * * 1-5'
```

```text
At 05:35 on every weekday (Monday through Friday).
```

```bash
cronlab explain '0 9 * * *'
```

```text
At 09:00 every day.
```

```bash
cronlab explain '*/15 * * * *'
```

```text
Every 15 minutes.
```

```bash
cronlab explain '0 0 1 1 *'
```

```text
At 00:00 on 1 January.
```

## Next

`--from` is exclusive. A run that lands exactly on the start instant is
skipped. Instants always include an offset.

```bash
cronlab next '0 9 * * *' --from '2026-10-04T00:00:00+01:00' --count 3
```

```text
2026-10-04T09:00:00+00:00
2026-10-05T09:00:00+00:00
2026-10-06T09:00:00+00:00
```

```bash
cronlab next '35 5 * * 1-5' --timezone Europe/London --from '2026-10-04T00:00:00+01:00' --count 5
```

```text
2026-10-05T05:35:00+01:00
2026-10-06T05:35:00+01:00
2026-10-07T05:35:00+01:00
2026-10-08T05:35:00+01:00
2026-10-09T05:35:00+01:00
```

A date that can never exist is valid syntax. `next` searches two years
from `--from` and then stops.

```bash
cronlab next '0 0 31 2 *' --from '2026-01-01T00:00:00Z' --count 1
```

```text
error: no runs within horizon
```

That command exits `1`.

## JSON

`--json` writes one object. Human errors stay on stderr when the flag is
off. With `--json`, failures still exit non-zero and put the error in the
envelope.

```bash
cronlab validate '35 5 * * 1-5' --json
```

```json
{"dialect": "vixie", "expression": "35 5 * * 1-5", "command": "validate", "timezone": "UTC", "from": null, "inclusive": false, "dst_policy": "skip_gap_first_fold", "horizon": {"years": 2}, "ok": true}
```

```bash
cronlab next '0 9 * * *' --from '2026-10-04T00:00:00+01:00' --count 3 --json
```

```json
{"dialect": "vixie", "expression": "0 9 * * *", "command": "next", "timezone": "UTC", "from": "2026-10-04T00:00:00+01:00", "inclusive": false, "dst_policy": "skip_gap_first_fold", "horizon": {"years": 2}, "ok": true, "runs": ["2026-10-04T09:00:00+00:00", "2026-10-05T09:00:00+00:00", "2026-10-06T09:00:00+00:00"], "count": 3}
```

## Dialect

Five fields, left to right: minute, hour, day-of-month, month,
day-of-week. Lists, ranges, and steps (`*/15`, `1-10/2`) are accepted.
Sunday is `0` or `7`.

When both day-of-month and day-of-week are not `*`, a time matches if
either field matches. That is the Vixie rule.

Seconds, `@daily` macros, `JAN` / `MON`, and `L` / `W` / `?` are
rejected.

## Time Policy

Cron fields are civil times in `--timezone` (default `UTC`). `--from` is
an absolute instant and must include an offset or `Z`. A naive datetime
is an error.

Nonexistent local times (spring-forward gaps) are skipped. A repeated
local time (autumn fold) is returned once, at the earlier offset.

## Exit Codes

| Result                                   | Stdout                         | Stderr     | Exit |
| ---------------------------------------- | ------------------------------ | ---------- | ---- |
| `validate` success                       | `valid`                        | empty      | `0`  |
| `explain` success                        | one or two sentences           | empty      | `0`  |
| `next` success                           | one ISO instant per line       | empty      | `0`  |
| `--version`                              | `cronlab` plus the version     | empty      | `0`  |
| Parse, validation, timezone, or `--from` | empty, or JSON with `ok:false` | `error: …` | `2`  |
| No run inside the two-year horizon       | empty, or JSON with `ok:false` | `error: …` | `1`  |

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
