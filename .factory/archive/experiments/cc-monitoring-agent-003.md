---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 003
verdict: KEEP
score_delta: +0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #003: Pane content capture + agent state detection

## Hypothesis
Implement pane content capture via tmux capture-pane and regex-based state detection for both Claude Code and OpenCode agents.

## Result
**KEEP** — score held at 1.0 (all eval dimensions passing, +0.0 delta)

## What Changed
- `src/cc_monitor/analyzer.py` (67 lines) — New module with:
  - `capture_pane()` — runs `tmux capture-pane -p -t {pane_id}` to grab terminal content
  - `detect_claude_state()` — regex matching for idle (❯ prompt), working (⏺ tool calls), waiting (✻ completion markers)
  - `detect_opencode_state()` — detects OpenCode Bubble Tea TUI timer patterns
  - `detect_state()` — orchestrator dispatching to agent-specific detector
- `tests/test_analyzer.py` (172 lines) — 17 new tests covering:
  - All 3 states (idle, working, waiting_for_input) for both Claude Code and OpenCode
  - Edge cases: empty pane, unknown agent type
  - Subprocess mocking for capture_pane

## Test Summary
- 39 total tests passing (22 from Phase 2 + 17 new)
- mypy clean, ruff lint+format clean

## CEO Verdict
PROCEED — State detection implemented with regex patterns matching research findings. 17 new tests with representative pane content. No issues found.

## Next Phase
Phase 4 — Activity summarization

## Links
- Project: cc-monitoring-agent
- Commit: d693382
