---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 16
verdict: revert
score_delta: -0.016
date: 2026-05-07
source: factory-archivist
---

# Experiment #022 (ID 16): Desktop notifications via terminal-notifier — no new modules (Cycle 4 H3)

## Hypothesis
Add desktop alert on `needs_input` state change via `terminal-notifier` in the watch loop. No new modules: embed `notify()` and `detect_transitions()` directly in `watch.py`, add `--notify` flag.

## Result
**REVERT** — score changed from ~0.575 to ~0.559 (-0.016)

## What Changed
- **Modified `src/cc_monitor/watch.py`**: added `notify()` function using `terminal-notifier`, `detect_transitions()` for state change tracking, `--notify` flag
- **10 new tests** for notification and transition detection
- No new modules created

## Root Cause of Failure
Lint regression: lint dimension dropped from 1.0 to 0.8, accounting for most of the -0.016 score delta. The notification implementation introduced lint issues that weren't caught before PR submission. This is a code quality failure, not a systemic blocker — the first genuine code-caused regression in cycle 4.

## Links
- Project: cc-monitoring-agent
- Issue: #29
- PR: (created but reverted)
