---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: "013 (factory ID 7)"
verdict: REVERT
score_delta: "-0.049"
date: 2026-05-07
source: factory-archivist
---

# Experiment #013: Add one-line summary mode for tmux status bar (Cycle 2, H2)

## Hypothesis
Add one-line summary mode (`ccm summary` / `--oneline`) for tmux status bar integration. Targets `capability_surface` dimension (0.31 — weakest dimension).

## Result
**REVERT** — factory composite score regressed (delta -0.049). Reverted due to precheck failure: score_direction and scope failures.

## What Changed
- Added `ccm summary` subcommand with compact single-line output
- Designed for tmux status bar integration (`#(ccm summary)`)

## Why Reverted
Precheck failed with score regression (delta -0.049). Root cause is **systemic** — identical to experiment #012:

- **E2E tests passed** — feature was functionally correct
- **Score regression was eval-systemic** — factory eval runs mypy/lint with system Python (not `uv run`), cannot resolve `cc_monitor` imports in src-layout
- New Python code added more import surface, amplifying existing eval detection failure
- `type_check` dimension drops to 0.0 on experiment branches due to unresolvable imports

## Analysis
Second of three consecutive reverts in cycle 2, all caused by the same systemic eval issue. The implementation was correct (tests pass, project eval 1.0), but the factory eval infrastructure cannot score src-layout projects correctly. This pattern makes all EXPLOIT/EXPLORE hypotheses that add new Python code unviable until the factory eval is fixed.

## Links
- Project: cc-monitoring-agent
- Issue: #12
- PR: none (reverted before PR)
- Factory ID: 7
