---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 2 Complete)

## Outcome

**ALL 3 HYPOTHESES REVERTED** — Cycle 2 produced zero kept experiments. Every implementation was functionally correct but reverted due to systemic factory eval limitations.

## Cycle 2 Results

| # | Hypothesis | Factory ID | Verdict | Score Delta | E2E | Project Eval |
|---|---|---|---|---|---|---|
| H1 | Filtering/sorting flags (`--state`, `--agent`, `--sort`) | 6 | REVERT | -0.058 | pass | 1.0 |
| H2 | One-line summary mode (`ccm summary`) | 7 | REVERT | -0.049 | pass | 1.0 |
| H3 | State change notifications (`--notify`) | 8 | REVERT | -0.032 | pass | 1.0 |

**Keep rate**: 0% (0/3)
**Composite score on main**: 0.539 (unchanged — all reverted)

## Root Cause Analysis

The factory eval infrastructure runs overlay dimensions (mypy, lint) using system Python, not `uv run` or the project's virtual environment. For src-layout projects (`src/package_name/`), system Python cannot resolve project imports. Consequences:

1. `type_check` dimension drops to 0.0 on experiment branches (mypy finds 16+ errors from unresolvable imports)
2. Every new Python file adds more unresolvable imports, amplifying the false regression
3. Score delta inversely correlates with code addition size: more code → larger regression → more certain revert

This is confirmed by the delta pattern: -0.058 (largest code addition) > -0.049 > -0.032 (smallest code addition).

## What Was Lost

Three completed, tested features that would have improved capability_surface:
- Filtering and sorting for multi-session usability
- tmux status bar integration via one-line summaries
- macOS notifications for state transitions

All implementations passed: unit tests, e2e tests, project eval (1.0), smoke tests. The features are architecturally sound and could be re-applied once the eval blocker is resolved.

## Blocking Issue

**Further improve cycles on cc-monitoring-agent are blocked** until one of:
1. Factory eval is fixed to use `uv run` for mypy/lint overlay dimensions
2. A project-level workaround is found (e.g., making src-layout invisible to system Python's mypy)
3. The eval scoring model is changed to not penalize import resolution failures in src-layout projects

## Cumulative Project Stats

| Metric | Value |
|---|---|
| Total experiments | 15 |
| Kept | 11 |
| Reverted | 4 |
| Overall keep rate | 73% (11/15) |
| Cycle 1 keep rate | 80% (4/5) |
| Cycle 2 keep rate | 0% (0/3) |
| Tests | 81 |
| Coverage | 98% |
| Project eval | 1.0 |
| Factory composite | 0.539 |
