---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 009
verdict: KEEP
score_delta: "+0.0 (factory composite unchanged due to eval detection issue)"
date: 2026-05-07
source: factory-archivist
---

# Experiment #009: Configure pytest-cov and fix test/coverage detection (H2)

## Hypothesis
Configure pytest-cov for the project so the factory eval detects the test suite and coverage output. The factory eval reported "no test suite detected" (tests=0.5) and "no coverage tool detected" (coverage=0.5) despite 70 tests existing. Adding pytest-cov with proper `source_pkgs` config for the src-layout should make both dimensions detectable.

## Result
**KEEP** — factory composite score 0.517 → 0.517 (delta +0.0, eval detection issue persists), 98% test coverage achieved.

This is a retry of experiment #002 which was reverted due to a scope violation (pyproject.toml was not in the modifiable file list). The retry succeeded after first moving pyproject.toml into the modifiable scope (commit f66f5b2).

## What Changed
- `pyproject.toml` — config-only changes:
  - Added `pytest-cov` to dev dependencies
  - Added `[tool.pytest.ini_options]` with `addopts = "--cov=cc_monitor --cov-report=term-missing"`
  - Added `[tool.coverage.run]` with `source_pkgs = ["cc_monitor"]` (essential for src-layout)
  - Added `[tool.coverage.report]` with `show_missing = true`, `fail_under = 80`
- `uv.lock` — lockfile updated with pytest-cov dependency tree

## Verification
- `pytest tests/ --cov=cc_monitor --cov-report=term-missing` — 70 passed, 98% coverage
- All existing tests continue to pass
- Coverage config validated for src-layout (`source_pkgs` instead of `source`)

## Analysis
Config-only change with zero code modifications. The key insight from research was that src-layout projects require `source_pkgs` (not `source`) in `[tool.coverage.run]` — using `source` would fail to find the package under `src/`. The 98% coverage confirms the test suite written during build phase was comprehensive.

The factory composite score did not move (+0.0) because the factory eval still has a systemic detection issue — it cannot find the test suite or coverage output despite both being properly configured. This is a known issue from experiment #008 as well.

Note: This experiment required two attempts. Experiment #002 was reverted because `pyproject.toml` was outside the builder's modifiable scope. The scope was expanded (commit f66f5b2) before retrying as experiment #003/009.

## Links
- Project: cc-monitoring-agent
- Issue: #3
- PR: #5
- Branch: experiment/3-pytest-cov-config
- Related: Experiment #002 (reverted predecessor)
