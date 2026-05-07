---
tags:
  - factory
  - project
  - cc-monitoring-agent
source: factory-archivist
---

# Factory: cc-monitoring-agent

## Summary

A Python CLI tool that scans all tmux panes, detects running Claude Code and OpenCode sessions, and displays a dashboard showing: what each agent is doing, whether it's waiting for user input, and the tmux coordinates to jump there. MVP: single command, snapshot view, no daemon or persistence.

## Status

- **State**: complete (all 7 build phases delivered)
- **Current Score**: 1.0 (all eval dimensions at 1.0)
- **Experiments Run**: 7
- **Kept**: 7, **Reverted**: 0
- **Total Tests**: 70
- **Approved Phases**: 7 (all complete)

## Build Plan (CEO-Approved 2026-05-07)

| Phase | Description | Category | Priority | Status |
|-------|-------------|----------|----------|--------|
| 1 | Project scaffold + eval harness | FIX | high | **DONE** (score 0.0 -> 1.0) |
| 2 | Data model + tmux discovery | EXPLORE | high | **DONE** (score 1.0 -> 1.0) |
| 3 | Pane capture + state detection | EXPLORE | high | **DONE** (score 1.0 -> 1.0) |
| 4 | Activity summarization | EXPLORE | high | **DONE** (score 1.0 -> 1.0) |
| 5 | Rich table display + CLI wiring | EXPLORE | high | **DONE** (score 1.0 -> 1.0) |
| 6 | Structured logging | EXPLOIT | medium | **DONE** (score 1.0 -> 1.0) |
| 7 | Integration tests + validation | EXPLOIT | medium | **DONE** (score 1.0 -> 1.0) |

## Research Phase (2026-05-07)

- **CEO Verdict**: PROCEED
- Research grounded in live system observation
- Two-tier detection strategy confirmed (fast path + child process verification)
- Minimal tech stack: subprocess + rich (no libtmux)
- Architecture: discover -> analyze -> display pipeline

## Source Notes

- [tmux Session Discovery](sources/tmux-session-discovery.md) — Two-tier detection strategy for finding Claude Code and OpenCode in tmux panes
- [Pane Content Capture](sources/pane-content-capture.md) — tmux capture-pane approach, ~5-10ms per pane
- [Claude Code Terminal Patterns](sources/claude-code-terminal-patterns.md) — Markers for idle/working/needs-input states
- [OpenCode Terminal Patterns](sources/opencode-terminal-patterns.md) — Bubble Tea TUI markers for state detection
- [Tech Stack Recommendation](sources/tech-stack-recommendation.md) — subprocess + rich, architecture pattern and data model
- [Similar Projects](sources/similar-projects.md) — No direct equivalent found, novel tool

## Strategy Snapshots

- [Post-Research Strategy (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07.md) — CEO PROCEED verdict, two-tier detection, minimal deps, linear pipeline
- [Build Plan Approved (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-build-plan.md) — 7-phase sequential build plan, all phases CEO-approved
- [Phase 1 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase1-complete.md) — Scaffold delivered, score 0.0 -> 1.0
- [Phase 2 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase2-complete.md) — Data model + discovery delivered, 22 tests, CEO PROCEED
- [Phase 3 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase3-complete.md) — Analyzer delivered, 39 tests, CEO PROCEED
- [Phase 4 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase4-complete.md) — Summarization delivered, 56 tests, CEO PROCEED
- [Phase 5 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase5-complete.md) — Display + CLI delivered, 62 tests, CEO PROCEED
- [Phase 6 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase6-complete.md) — Structured logging delivered, 62 tests, CEO PROCEED
- [Phase 7 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-phase7-complete.md) — Integration tests delivered, 70 tests, BUILD COMPLETE

## Recent Experiments

- [Experiment #001](experiments/cc-monitoring-agent-001.md) — Project scaffold + eval harness (**KEEP**, +1.0)
- [Experiment #002](experiments/cc-monitoring-agent-002.md) — Data model + tmux pane discovery (**KEEP**, +0.0)
- [Experiment #003](experiments/cc-monitoring-agent-003.md) — Pane capture + state detection (**KEEP**, +0.0)
- [Experiment #004](experiments/cc-monitoring-agent-004.md) — Activity summarization (**KEEP**, +0.0)
- [Experiment #005](experiments/cc-monitoring-agent-005.md) — Rich table display + CLI wiring (**KEEP**, +0.0)
- [Experiment #006](experiments/cc-monitoring-agent-006.md) — Structured logging with loguru (**KEEP**, +0.0)
- [Experiment #007](experiments/cc-monitoring-agent-007.md) — Integration tests + validation (**KEEP**, +0.0)
