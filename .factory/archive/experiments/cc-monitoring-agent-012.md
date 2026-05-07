---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: "012 (factory ID 6)"
verdict: REVERT
score_delta: "-0.058"
date: 2026-05-07
source: factory-archivist
---

# Experiment #012: Add filtering/sorting flags to status subcommand (Cycle 2, H1)

## Hypothesis
Add filtering and sorting flags (`--state`, `--agent`, `--sort`) to the `status` subcommand for usability with many sessions. Targets `capability_surface` dimension (0.31 — weakest dimension).

## Result
**REVERT** — factory composite score regressed from 0.539 to 0.481 (delta -0.058). Reverted due to precheck failure: score_direction and scope failures.

## What Changed
- Added `--state`, `--agent`, `--sort` flags to status subcommand
- Filtering and sorting logic for session list output

## Why Reverted
The precheck failed with score regression (0.539 → 0.481, delta -0.058). Root cause is **systemic**, not a code quality issue: the factory eval runs mypy/lint as overlay dimensions using the system Python, which cannot resolve project imports in the src-layout. The experiment branch's new code added more import surface, amplifying the existing eval detection failure.

Key details:
- **E2E tests passed** — the feature itself was functionally correct
- **Score regression was eval-systemic** — factory eval uses system Python (not `uv run`), so mypy/lint overlays fail to resolve `cc_monitor` imports
- **Same failure pattern** as cycle 1 experiments (all scored +0.0 due to eval detection issues), but this time the delta went negative because main had merged cycle 1 work that shifted the baseline

## Analysis
This is the second revert for this project (first was scope violation in experiment #002). Unlike the scope violation, this revert is caused by a systemic factory eval issue that affects all experiments adding new Python code to src-layout projects. The code itself was correct and tests passed.

The negative delta is misleading — it reflects eval infrastructure limitations, not code quality regression. The factory eval's mypy/lint overlays execute with system Python, which lacks the project's venv dependencies. More code = more unresolvable imports = worse overlay scores.

## Pattern Extracted
Factory eval systemic regression — src-layout projects scored with system Python suffer import resolution failures on mypy/lint overlay dimensions. New code amplifies the false-negative. See patterns.md.

## Links
- Project: cc-monitoring-agent
- Issue: #10
- PR: none (reverted before PR)
- Factory ID: 6
- Predecessor: Experiment #011 (last kept experiment)
