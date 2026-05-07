---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: "002 (factory ID 2)"
verdict: REVERT
score_delta: "+0.0"
date: 2026-05-07
source: factory-archivist
---

# Experiment #002 (Revert): Configure pytest-cov — scope violation

## Hypothesis
Configure pytest-cov for the project so the factory eval detects the test suite and coverage output. Add `pytest-cov` to dev deps and `[tool.coverage.run]` with `source_pkgs` for src-layout.

## Result
**REVERT** — change was correct but `pyproject.toml` was not in the builder's modifiable file list. The factory scope guard rejected the diff before it could be evaluated.

## What Changed
- `pyproject.toml` — attempted config-only changes (pytest-cov dep, coverage config)
- No code changes

## Why Reverted
The builder produced a valid patch, but `pyproject.toml` was listed as read-only in `factory.md`. The CEO reverted the experiment because the scope violation made the change unshippable regardless of correctness.

## Resolution
- Scope was expanded in commit f66f5b2 (added `pyproject.toml` to modifiable files)
- Experiment was retried as factory ID 3, archived as experiment #009 — **KEEP**, 98% coverage achieved

## Pattern Extracted
This failure led to cross-project pattern: "Scope violations cause avoidable reverts — expand modifiable scope proactively" (see patterns.md).

## Links
- Project: cc-monitoring-agent
- Issue: #3
- Successor: Experiment #009 (factory ID 3)
