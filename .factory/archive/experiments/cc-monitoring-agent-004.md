---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 004
verdict: KEEP
score_delta: +0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #004: Activity summarization

## Hypothesis
Extract one-sentence activity summaries from captured pane content for both Claude Code and OpenCode agents, using recap extraction, tool call detection, thinking state, and completion markers.

## Result
**KEEP** — score held at 1.0 (all eval dimensions passing, +0.0 delta)

## What Changed
- `src/cc_monitor/analyzer.py` — Extended with:
  - `summarize_claude_activity()` — recap extraction, tool call name detection, thinking state, completion duration, fallback chain
  - `summarize_opencode_activity()` — timer-based processing status, content extraction, active session fallback
  - `summarize_activity()` — dispatcher by agent_type
  - `analyze_sessions()` — orchestrator that captures pane, detects state, and summarizes for each session
  - Compiled regex patterns for recap, tool names, completion duration, decoration lines
- `tests/test_analyzer.py` — 17 new tests covering:
  - Claude: recap, tool call, thinking, completion, fallback, empty, decoration-only
  - OpenCode: working with timer, idle content, empty, decoration fallback
  - Dispatch: claude/opencode routing, unknown agent type
  - Integration: single session update, empty capture, multiple sessions

## Test Summary
- 56 total tests passing (39 from Phase 3 + 17 new)
- mypy clean, ruff lint+format clean

## CEO Verdict
PROCEED — Summarization pipeline clean. Recap extraction, tool call detection, thinking state, completion markers, fallback chain all implemented. `analyze_sessions` ties it all together. No issues found.

## Next Phase
Phase 5 — Rich table display + CLI wiring

## Links
- Project: cc-monitoring-agent
- Commit: 6922610
