---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 002
verdict: KEEP
score_delta: +0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #002: Data model + tmux pane discovery

## Hypothesis
Define AgentSession data model and implement tmux pane discovery with two-tier detection (fast path + child process verification).

## Result
**KEEP** — score held at 1.0 (all eval dimensions passing, +0.0 delta)

## What Changed
- `src/cc_monitor/models.py` — AgentSession dataclass with typed fields for session tracking
- `src/cc_monitor/discovery.py` — Full discovery pipeline:
  - `list_all_panes()` parses tmux list-panes output
  - `classify_pane()` with two-tier detection: opencode direct match, version regex for Claude candidates
  - `verify_claude_candidate()` checks child processes via ps
  - `discover_sessions()` orchestrator returning list[AgentSession]
- `tests/test_discovery.py` — 22 tests total covering:
  - Pane parsing and classification
  - Child process verification
  - discover_sessions integration with mocked subprocess
  - Edge cases: no tmux, malformed lines, version pane without claude child

## CEO Verdict
PROCEED — Data model and discovery pipeline implemented correctly. Two-tier detection strategy matches research. No issues found.

## Next Phase
Phase 3 — Pane content capture + state detection

## Links
- Project: cc-monitoring-agent
- Commit: 53072ac
