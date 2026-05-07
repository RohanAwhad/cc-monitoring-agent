---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 21
verdict: keep
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #027: Add ccm attach subcommand for quick-jump navigation

## Hypothesis
Add ccm attach subcommand for quick-jump navigation to agent tmux panes.

## Result
**KEEP** — score unchanged at 1.0 (delta 0.0). Project eval 1.0. PR #40 open for review.

## What Changed
- Added `_run_attach(args)` handler and `attach` subparser in `cli.py` (+38 lines)
- Support exact tmux target match and case-insensitive partial match against tmux_target, agent_type, and session_name
- Print numbered list on multiple matches, error on no match
- 6 new tests in `test_basic.py` (+114 lines): exact target, partial agent type, partial session name, no match, multiple matches, case-insensitive matching
- No new files created — follows validated no-new-files pattern from cycle 5
- Total: 2 files changed, 152 insertions, 3 deletions

## Context
- Cycle 6, Hypothesis 1 (of 2)
- Category: EXPLORE targeting capability_surface
- Every competitor (TmuxCC, ATM, Workmux) offers quick-jump — this closes a capability gap
- Researcher ranked attach as #1 by value/effort ratio
- Follows no-new-files pattern validated in cycle 5 (3/3 KEPT)

## Links
- Project: cc-monitoring-agent
- Issue: #39
- PR: #40
- Branch: experiment/21-ccm-attach
