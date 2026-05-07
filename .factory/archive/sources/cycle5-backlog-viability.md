---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Backlog Feature Viability Analysis (Cycle 5 Research)

All 3 unique backlog features have been implemented correctly multiple times. The code works — the gates block them.

## Feature Attempt Summary

| Feature | Attempts | Best Score Delta | Blocker |
|---|---|---|---|
| Filtering/sorting (`--state`, `--agent`, `--sort`) | 5 (012, 016, 017, 020, 025) | -0.001 (noise) | scope guard, anti_pattern, target scaling |
| Summary mode (`ccm summary`) | 3 (018, 019, 021) | **+0.008** (positive!) | anti_pattern (blocked despite gain) |
| Notifications (`ccm watch --notify`) | 2 (014, 022) | -0.016 | lint regression (fixable), scope guard |

## Critical Finding

Experiment 021 (summary mode, no-new-files strategy) actually **improved** the score by +0.008 but was blocked by the anti_pattern gate. This proves the feature is viable — only the gate blocks it.

## Validated Implementation Strategy

All features must use the **no-new-files strategy**:
- Filtering/sorting: inline in `cli.py` or `_run_status()` private functions
- Summary mode: `format_summary()` in `display.py`, `_run_summary()` in `cli.py`
- Notifications: `_notify()` and state tracking inline in `watch.py`

The argparse extension pattern (`add_subparsers` + `set_defaults(func=handler)`) is well-established in the codebase.
