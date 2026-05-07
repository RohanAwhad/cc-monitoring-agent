---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Phase 2 Complete)

## Phase 2 Outcome
Data model and tmux discovery pipeline delivered. CEO verdict: PROCEED.

## Architecture Confirmed
- **AgentSession dataclass** — minimal typed fields for session tracking
- **Two-tier detection** — fast regex match for opencode, version regex + child process verify for Claude Code
- **Pipeline pattern** — list_all_panes → classify_pane → verify_claude_candidate → discover_sessions

## Test Coverage
22 tests covering the full detection flow including edge cases (no tmux, malformed input, false positives from version panes).

## Score Trajectory
- Phase 1: 0.0 → 1.0 (scaffold + eval harness)
- Phase 2: 1.0 → 1.0 (data model + discovery, all evals still passing)

## Next: Phase 3
Pane content capture + state detection. Will use `tmux capture-pane` to read pane contents and apply pattern matching from research (Claude Code terminal patterns, OpenCode TUI markers) to determine agent state (idle/working/needs-input).
