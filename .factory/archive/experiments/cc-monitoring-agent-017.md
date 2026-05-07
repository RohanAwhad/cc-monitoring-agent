---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 11
verdict: revert
score_delta: -0.001
date: 2026-05-07
source: factory-archivist
---

# Experiment #11: Add filtering and sorting flags (retry with mypy fix)

## Hypothesis
Retry of experiment #10 — add `--state`, `--agent`, `--sort` flags to status subcommand, this time with additional mypy annotation fixes to prevent type_check regression.

## Result
**REVERT** — score changed from 0.537 to 0.536 (-0.001). Precheck failed on score_direction, scope, and anti_pattern.

## What Changed
- Same filtering/sorting flags as experiment #10
- Additional mypy-compatible annotations attempted
- Reverted due to three precheck failures: score_direction (marginal regression), scope guard, and anti_pattern (too similar to experiment #10)

## Root Cause
Two distinct blockers:
1. **Score noise**: -0.001 delta is within noise range but still fails the score_direction precheck (which requires delta >= 0)
2. **Anti-pattern detection**: Factory precheck flagged this as too similar to experiment #10, which was already reverted. The anti_pattern guard prevents repeating the same failing approach

## Key Observations
1. The anti_pattern precheck is correctly preventing wasted cycles — retrying the same code change that caused a score regression is unlikely to produce a different result
2. Score noise at the ±0.001 level means the factory composite is effectively insensitive to capability_surface improvements when overlay dimensions are broken
3. This experiment confirmed that the filtering/sorting feature cannot pass factory eval until overlay detection is fixed

## Links
- Project: cc-monitoring-agent
- Issue: #17
