---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 9
verdict: keep
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #9: Fix eval blocker (mypy_path=src) and merge 4 open PRs to main

## Hypothesis
Two-step operational fix: (1) Add `mypy_path = "src"` to `[tool.mypy]` in pyproject.toml to unblock factory eval's system Python mypy resolution. (2) Merge 4 open PRs (#2 mypy fix, #5 pytest-cov, #7 watch mode/subcommands, #9 observability) to main in dependency order, resolving merge conflicts at each step.

## Result
**KEEP** — operational experiment, precheck skipped. Project eval 1.0 (81 tests, 97% coverage, mypy clean, lint clean). Factory composite still 0.537 due to remaining overlay dimension issues (system Python can't find loguru/rich stubs for type_check, tests/coverage "not detected" by factory eval).

## What Changed
- Added `mypy_path = "src"` to `[tool.mypy]` in pyproject.toml — 1-line config fix
- Merged PR #2 (mypy strict-mode type fixes) to main
- Merged PR #5 (pytest-cov configuration, 98% coverage) to main
- Merged PR #7 (watch mode with Rich Live, subcommand refactor) to main
- Merged PR #9 (observability expansion, scan_id tracing, structured JSON logs) to main
- Resolved merge conflicts in PR #9 where its older branch diverged from changes in PRs #2 and #7 — preserved type-safe signatures and subcommand structure while integrating observability logging

## Key Observations
1. **Conflict resolution was the main challenge**: PR #9 was branched before PRs #2 and #7 merged, so it had older function signatures (broad `str` types instead of `Literal` types) and lacked the subcommand structure. Builder correctly kept the newer type-safe code.
2. **Project eval vs factory eval gap persists**: Project eval shows 1.0 (perfect), but factory composite is 0.537. The `mypy_path` fix resolved project-level mypy but factory eval's system Python still can't find third-party stubs (loguru, rich).
3. **Factory eval type_check dropped from 0.4 to 0.3**: 14 errors now (was 12) — the additional errors are import-not-found for loguru/rich stubs, introduced by merging PRs #9 and #7 which add more imports of those libraries. This is a factory infrastructure issue, not a project code issue.
4. **Tests/coverage still "not detected"**: Factory eval doesn't detect the test suite or coverage despite both being fully functional. This is another factory overlay limitation.

## Quantitative Summary
- **Project eval**: 1.0 (perfect)
- **Factory composite**: 0.537 (essentially unchanged from 0.539)
- **Tests**: 81 passing
- **Coverage**: 97%
- **mypy (project)**: 0 errors
- **mypy (factory)**: 14 errors (all import-not-found for third-party stubs)
- **PRs merged**: 4 (#2, #5, #7, #9)
- **Issue**: #16

## Links
- Project: cc-monitoring-agent
- Issue: #16
- PR: direct merge (no PR — operational merge workflow)
