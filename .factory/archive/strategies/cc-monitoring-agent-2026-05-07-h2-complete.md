---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 H2 Complete

## Experiment Outcome
H2 (Configure pytest-cov and fix test/coverage detection) — **KEEP**

## What Happened
- First attempt (experiment #002) was reverted due to scope violation: `pyproject.toml` was not in the builder's modifiable file list
- Scope was expanded by adding `pyproject.toml` to factory config (commit f66f5b2)
- Second attempt (experiment #003, archived as #009) succeeded: pytest-cov configured, 98% coverage achieved
- Factory composite score unchanged at 0.517 due to persistent eval detection issue

## Key Config Decisions
- Used `source_pkgs = ["cc_monitor"]` (not `source`) — required for src-layout projects
- Set `fail_under = 80` as coverage floor
- Added `--cov=cc_monitor --cov-report=term-missing` to pytest addopts

## Improve Cycle Progress
- H1: Fix mypy strict-mode errors — **DONE** (KEEP)
- H2: Configure pytest-cov — **DONE** (KEEP, 98% coverage)
- H3: Watch mode with Rich Live — PENDING
- H4: Expand observability — PENDING

## Next Steps
H3 (watch mode) is the next priority — highest expected impact on capability_surface dimension.
