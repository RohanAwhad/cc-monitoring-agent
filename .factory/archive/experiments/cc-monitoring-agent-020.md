---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 14
verdict: revert
score_delta: -0.003
date: 2026-05-07
source: factory-archivist
---

# Experiment #020 (ID 14): Filtering/sorting flags + full observability bundle (Cycle 4 H1)

## Hypothesis
Add `--state`, `--agent`, `--sort` flags to status subcommand AND instrument all 17 previously uninstrumented functions with `logger.debug()` across 5 modules. Bundle strategy: improve capability_surface + observability simultaneously.

## Result
**REVERT** — score changed from 0.575 to 0.572 (-0.003)

## What Changed
- **New file `src/cc_monitor/filtering.py`**: `filter_sessions()` and `sort_sessions()` functions with full type hints
- **Modified `src/cc_monitor/cli.py`**: added `--state`, `--agent`, `--sort` flags to status subparser, integrated filtering/sorting into status output
- **Observability bundle**: added `logger.debug()` to all 17 previously uninstrumented functions across analyzer.py, discovery.py, cli.py, watch.py, logging.py — function coverage 32% → 100%
- **New test file `tests/test_filtering.py`**: 6 unit tests for filter logic, 4 unit tests for sort logic, 4 CLI integration tests for new flags
- **Eval**: project eval 1.0, 95 tests passing, 97% coverage, lint/typecheck/format clean

## Root Cause of Failure
The `capability_surface` dimension uses formula `max(100, modules * 10)` for its target. Adding a new module (`filtering.py`) increased the target denominator faster than the numerator (new public functions). Net effect: capability_surface score dropped despite adding more actual functionality. The observability improvement (+0.27) was insufficient to offset.

## Key Context
- 5th attempt at filtering/sorting (cycle 2 #012, cycle 3 #016, cycle 3 #017, cycle 4 #020)
- First attempt with bundle strategy and lowered threshold (0.56)
- Bundle strategy partially validated: observability improved 0.53 → 0.80, but capability_surface target scaling punished the new module

## Links
- Project: cc-monitoring-agent
- Issue: #25
- PR: #26
