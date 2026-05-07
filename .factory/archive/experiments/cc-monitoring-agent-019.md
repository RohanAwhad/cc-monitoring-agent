---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 13
verdict: revert
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #13: Add one-line summary mode (ccm summary) — retry

## Hypothesis
Retry of experiment #12 — add `ccm summary` subcommand for one-line tmux status bar integration, with clean working tree.

## Result
**REVERT** — precheck failed. Score 0.572 vs threshold 0.800. The 0.800 threshold is mathematically unachievable given current factory eval dimension caps.

## What Changed
- Summary mode implemented correctly — e2e tests pass, project eval functional
- Clean PR created (no dirty factory files)
- Precheck rejected because factory composite (0.572) cannot reach the 0.800 threshold

## Root Cause — Systemic Blocker Analysis
The factory eval threshold (0.800) is **mathematically unachievable** for this project. The maximum possible score is approximately **0.645**, broken down:

| Dimension | Current | Max Possible | Blocker |
|---|---|---|---|
| type_check | ~0.3 | ~0.7 | System Python can't find loguru/rich stubs |
| tests | 0.5 | 0.5 | Factory eval doesn't detect pytest suite |
| coverage | 0.5 | 0.5 | Factory eval doesn't detect coverage config |
| research_grounding | 0.0 | 0.0 | Dimension not scored for this project type |
| capability_surface | ~0.4 | 1.0 | Only dimension fully controllable |
| observability | ~0.7 | 1.0 | Partially controllable |
| lint | 1.0 | 1.0 | Clean |

Even with perfect scores on controllable dimensions, the broken overlay dimensions (tests=0.5, coverage=0.5, research_grounding=0.0) cap the composite well below 0.800.

## Key Observations
1. **This is the definitive proof** that cc-monitoring-agent cannot improve further under current factory eval infrastructure
2. The score actually improved slightly (0.537 → 0.572) indicating the code was beneficial, but the precheck threshold blocks it
3. All 4 post-H1 experiments (10-13) were reverted despite correct implementations — 0% keep rate
4. The project is functionally complete (project eval 1.0, 81 tests, 97% coverage) but factory eval can't measure it

## Links
- Project: cc-monitoring-agent
- Issue: #20
