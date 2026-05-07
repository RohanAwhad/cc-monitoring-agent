---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 22
verdict: keep
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #028: Token/cost estimation from Claude Code conversation files

## Hypothesis
Add token/cost estimation from Claude Code conversation files via --costs flag, enabling users to see estimated token usage and API costs per session.

## Result
**KEEP** — score remained at 1.0 (delta 0.0)

## What Changed
- Added `estimate_session_cost()` function in `analyzer.py` to parse Claude Code conversation JSONL files and estimate token counts and costs
- Added `--costs` flag to CLI for enabling cost estimation display
- Added `cwd` field to `AgentSession` data model for tracking session working directories
- Added cost-related display columns to the dashboard output
- 11 new tests covering cost estimation logic

## Links
- Project: cc-monitoring-agent
- PR: #42
- Experiment ID: 22
- Cycle: 6 (H2)
