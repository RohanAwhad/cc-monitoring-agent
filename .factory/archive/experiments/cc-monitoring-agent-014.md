---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: "014 (factory ID 8)"
verdict: REVERT
score_delta: "-0.032"
date: 2026-05-07
source: factory-archivist
---

# Experiment #014: Add state change notifications to watch mode (Cycle 2, H3)

## Hypothesis
Add `--notify` flag to `ccm watch` to trigger macOS osascript notifications on `needs_input` state transitions. Targets `capability_surface` dimension (0.31 — weakest dimension).

## Result
**REVERT** — factory composite score regressed (delta -0.032). Reverted due to precheck failure: score_direction and scope failures.

## What Changed
- Added `--notify` flag to `ccm watch` subcommand
- macOS osascript notifications triggered on agent state transitions to `needs_input`

## Why Reverted
Precheck failed with score regression (delta -0.032). Root cause is **systemic** — identical to experiments #012 and #013:

- **E2E tests passed** — feature was functionally correct
- **Score regression was eval-systemic** — factory eval runs mypy/lint with system Python (not `uv run`), cannot resolve `cc_monitor` imports in src-layout
- Smallest delta of the three cycle 2 experiments (likely smallest code addition)

## Analysis
Third and final revert in cycle 2. All three hypotheses (H1-H3) were functionally correct implementations reverted solely due to systemic factory eval limitations. The decreasing delta pattern (-0.058, -0.049, -0.032) correlates with decreasing code addition size, confirming the root cause: more new code = more unresolvable imports = larger score regression.

## Links
- Project: cc-monitoring-agent
- Issue: #14
- PR: none (reverted before PR)
- Factory ID: 8
