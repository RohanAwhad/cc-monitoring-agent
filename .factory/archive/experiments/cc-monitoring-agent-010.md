---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 010
verdict: KEEP
score_delta: "+0.0 (factory composite unchanged due to eval detection issue)"
date: 2026-05-07
source: factory-archivist
---

# Experiment #010: Add watch mode with Rich Live — ccm watch (H3)

## Hypothesis
Add a `ccm watch` subcommand that continuously monitors Claude Code and OpenCode sessions using Rich Live for flicker-free terminal updates. This targets the `capability_surface` eval dimension (currently 0.3143, surface=44, target=140) by adding a new module, new public functions, and a new CLI entry point.

## Result
**KEEP** — factory composite score 0.517 → 0.517 (delta +0.0, eval detection issue persists). Project eval 1.0. 81 tests pass (8 new). CEO verdict: PROCEED.

## What Changed
- `src/cc_monitor/watch.py` — New module implementing watch mode:
  - `run_watch_loop()` — Main entry point using Rich Live for continuous dashboard refresh
  - Configurable refresh interval (default 2s)
  - Graceful Ctrl+C handling
- `src/cc_monitor/cli.py` — Refactored from single command to argparse subcommands:
  - `ccm status` — Original snapshot view (default when no subcommand given)
  - `ccm watch` — New continuous monitoring mode
  - Backward compatibility preserved: bare `ccm` defaults to `status`
- `src/cc_monitor/display.py` — `STATE_STYLES` dict renamed for reuse by watch module (minimal change)
- `tests/test_watch.py` — 8 new tests covering watch mode functionality

## Verification
- 81 tests pass (70 existing + 8 new + 3 integration)
- Project eval: 1.0
- CEO review: clean, no issues found
- Backward compatibility: bare `ccm` still works as before

## Analysis
This is the highest-impact improve experiment so far in terms of new capability surface: a new module (watch.py), new public functions, and a new subcommand entry point. The subcommand refactor in cli.py was well-scoped — it preserves backward compatibility while establishing the pattern for future subcommands (filtering, sorting, etc.).

The factory composite score still did not move (+0.0) due to the persistent eval detection issue. The `capability_surface` dimension should have improved (new module + new public functions + new entry point increases the surface count), but the factory eval may not be re-evaluating correctly.

Growth target: `capability_surface` (0.3143 → should increase with new module/functions).

## Links
- Project: cc-monitoring-agent
- Issue: #6
- PR: #7
- Branch: experiment/4-watch-mode
- Commit: d52fb9e
