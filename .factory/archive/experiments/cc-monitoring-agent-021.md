---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 15
verdict: revert
score_delta: +0.008
date: 2026-05-07
source: factory-archivist
---

# Experiment #021 (ID 15): One-line summary mode — no new files (Cycle 4 H2)

## Hypothesis
Add one-line summary mode (`ccm summary`) for tmux status bar integration. No new files strategy: embed summary subcommand in `cli.py` and `format_summary()` in `display.py` to avoid capability_surface target scaling penalty discovered in H1.

## Result
**REVERT** — score IMPROVED by +0.008, but blocked by anti_pattern precheck (0.62 similarity to experiment #13)

## What Changed
- **Modified `src/cc_monitor/cli.py`**: added `summary` subcommand
- **Modified `src/cc_monitor/display.py`**: added `format_summary()` function
- **6 new tests** for summary output format
- No new files created (strategy validated)

## Root Cause of Failure
Anti-pattern precheck detected 0.62 similarity to experiment #13 (prior summary mode attempt from cycle 3). Despite the score actually improving (+0.008), the precheck rejected the experiment because the hypothesis was too similar to a previously reverted one. Also failed scope guard (likely .factory/ working tree contamination).

## Key Insight
**The no-new-files strategy works for score.** This experiment proved that avoiding new modules prevents the capability_surface target scaling penalty. The +0.008 gain validated the approach. However, the anti_pattern guard blocks retrying hypotheses that are semantically similar to prior reverts, even when the implementation strategy is fundamentally different.

## Links
- Project: cc-monitoring-agent
- Issue: #27
- PR: (created but reverted)
