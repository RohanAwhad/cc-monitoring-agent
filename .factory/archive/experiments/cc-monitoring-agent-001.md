---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 001
verdict: KEEP
score_delta: "+1.0"
date: 2026-05-07
source: factory-archivist
---

# Experiment #001: Project scaffold + eval harness

## Hypothesis

All 5 eval dimensions must pass before any feature work. Creating pyproject.toml, package structure, CLI stub, tests, and tooling configs gets the build green (composite score 0.0 → 1.0).

## Result

**KEEP** — score changed from 0.0 to 1.0 (+1.0)

All 5 eval dimensions now score 1.0:
- **tests** (40%): trivial passing test in place
- **typecheck** (25%): mypy passes, py.typed marker present
- **lint** (15%): ruff check passes
- **cli_runs** (15%): `__main__.py` with argparse prints help successfully
- **formatting** (5%): ruff format --check passes

## What Changed

- Created `pyproject.toml` with project metadata, `rich` dependency, dev deps (`pytest`, `mypy`, `ruff`)
- Created package structure: `src/cc_monitor/__init__.py`, `src/cc_monitor/__main__.py`, `src/cc_monitor/py.typed`
- Wired `__main__.py` with argparse for `--help` (satisfies cli_runs eval)
- Created `tests/__init__.py` and trivial passing test (satisfies tests eval)
- Added `.gitignore` and cleaned cached build artifacts
- All tooling (mypy, ruff check, ruff format) passes clean

## CEO Review

- **Verdict**: PROCEED
- **Rationale**: Scaffold is clean. All eval dimensions at 1.0. Good foundation.
- **Issues found**: None
- **Next step**: Phase 2 — data model + tmux discovery

## Links

- Project: cc-monitoring-agent
- Commits: `2b9ccec` (scaffold), `0e5fc9b` (gitignore cleanup)
