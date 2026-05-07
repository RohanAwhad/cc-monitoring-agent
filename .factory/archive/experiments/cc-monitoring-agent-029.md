---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 23
verdict: keep
score_delta: +0.003
date: 2026-05-07
source: factory-archivist
---

# Experiment #029 (ID 23): Add Gemini CLI and Codex CLI detection

## Hypothesis
Extend agent discovery and analysis to detect Gemini CLI and Codex CLI sessions in tmux panes, alongside existing Claude Code and OpenCode detection.

## Result
**KEEP** — score changed from 0.577 to 0.580 (+0.003)

## What Changed
- **Extended `agent_type`**: Added `gemini` and `codex` as recognized agent types
- **Modified `discovery.py`**: Added detection logic for Gemini CLI and Codex CLI processes
- **Modified `analyzer.py`**: Added state detection patterns for Gemini and Codex terminal output
- **15 new tests**: Coverage for new agent type detection and state analysis
- **Issue**: #43, **PR**: #44

## Key Observations
- First experiment with a positive score delta since cycle 4 H2 (+0.008, which was reverted for anti_pattern)
- Continues the no-new-files strategy from cycles 5-6 — all code embedded in existing modules
- Extends the KEEP streak to 6 consecutive experiments (cycle 5 H1 through cycle 7 H1)
- Precheck had a scope false positive but was overridden

## Links
- Project: [[cc-monitoring-agent]]
- Issue: #43
- PR: #44
