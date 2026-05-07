---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 10
verdict: revert
score_delta: -0.018
date: 2026-05-07
source: factory-archivist
---

# Experiment #10: Add filtering and sorting flags (--state, --agent, --sort)

## Hypothesis
Add `--state`, `--agent`, `--sort` flags to the status subcommand to allow users to filter and sort the agent dashboard output. Targeting capability_surface dimension growth.

## Result
**REVERT** — score changed from 0.537 to 0.519 (-0.018). Precheck failed on score_direction and scope.

## What Changed
- Added filtering flags (`--state`, `--agent`) to status subcommand
- Added sorting flag (`--sort`) for column-based sorting
- Code was functionally correct — e2e tests passed, project eval 1.0
- Reverted due to factory eval score regression

## Root Cause
Factory overlay `type_check` dimension regressed because new Python code introduced additional imports that system Python mypy couldn't resolve. The `mypy_path = "src"` fix (experiment #9/015) resolved project-level imports but factory eval's system Python still lacks third-party stubs (loguru, rich). Each new file with these imports amplifies the type_check penalty.

## Key Observations
1. This is the same hypothesis as cycle 2 experiment #012, retried after the mypy_path fix
2. The mypy_path fix helped (delta -0.018 vs -0.058 in cycle 2) but didn't fully resolve the systemic issue
3. The code implementation was identical in quality to cycle 2 — functionally correct, tests passing
4. Factory eval's overlay dimensions remain the bottleneck

## Links
- Project: cc-monitoring-agent
- Issue: #17
