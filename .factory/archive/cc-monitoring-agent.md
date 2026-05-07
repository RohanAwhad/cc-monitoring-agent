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

- **State**: improve (build complete, cycle 1 complete)
- **Current Score**: 0.517 (factory composite) / 1.0 (project eval)
- **Experiments Run**: 12 total (7 build + 5 improve), 1 reverted
- **Kept**: 11, **Reverted**: 1
- **Total Tests**: 81, **Coverage**: 98%
- **Build Phases**: 7/7 complete
- **Improve Cycle 1**: Complete — 4 hypotheses delivered (H1-H4), 5 experiments (4 kept, 1 reverted)
- **Note**: Factory composite score (0.517) diverges from project eval (1.0) due to eval detection issue — factory eval uses stale `last_eval.json` that predates the improve cycle fixes

## Score History

- **Build phase**: Internal eval 1.0, factory composite 0.517 (discrepancy due to stale eval cache)
- **H1 (mypy fix)**: Factory 0.517 → 0.517 (delta n/a, eval detection issue); project eval 1.0 — type_check dimension fixed (12 errors → 0)
- **H2 (pytest-cov)**: Factory 0.517 → 0.517 (delta +0.0, eval detection issue); 98% coverage achieved — pytest-cov configured with source_pkgs for src-layout
- **H3 (watch mode)**: Factory 0.517 → 0.517 (delta +0.0, eval detection issue); ccm watch subcommand added — Rich Live, subcommand refactor, 8 new tests, 81 total
- **H4 (observability)**: Factory 0.517 → 0.517 (delta +0.0, eval detection issue); scan_id tracing, structured JSON logs, debug logging in cli/display/models — function coverage 33% → 80%+
- **Remaining growth targets**: capability_surface (per factory eval dimensions)

## Improve Cycle 1 Summary (2026-05-07)

| Hypothesis | Category | Target Dimension | Verdict | Key Result |
|---|---|---|---|---|
| H1: Fix 12 mypy strict-mode errors | FIX | type_check (0.4 → 1.0) | **KEEP** | Single-file 10-line diff, all 12 errors resolved |
| H2: Configure pytest-cov (attempt 1) | EXPLOIT | tests/coverage | **REVERT** | Scope violation — pyproject.toml was read-only |
| H2: Configure pytest-cov (retry) | EXPLOIT | tests/coverage | **KEEP** | 98% coverage, source_pkgs for src-layout |
| H3: Watch mode (Rich Live) | EXPLOIT | capability_surface | **KEEP** | New module + subcommand, 8 new tests, backward compat |
| H4: Observability expansion | EXPLOIT | observability | **KEEP** | scan_id tracing, structured JSON, 33% → 80%+ coverage |

**Keep rate**: 80% (4/5)
**Lessons learned**: Expand modifiable scope *before* running experiments that touch config files.

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

## Improve Cycle — Research Findings (2026-05-07)

CEO Verdict: **PROCEED**. Research thorough and actionable.

### Prioritized Focus Areas (FEEC order)

1. **FIX**: Add pytest-cov and coverage configuration — make test quality measurable ✅ (H2)
2. **EXPLOIT**: Watch mode (`ccm watch`) — highest-impact feature, Rich Live, capability_surface growth ✅ (H3)
3. **EXPLOIT**: Filtering and sorting flags (`--state`, `--agent`, `--sort`)
4. **EXPLORE**: One-line summary mode for tmux/shell prompt integration
5. **EXPLORE**: State change notifications via macOS osascript

### CEO Priorities for Strategist

- FIX type_check (12 mypy errors, score 0.4) ✅ (H1)
- EXPLOIT watch mode — highest growth impact on capability_surface ✅ (H3)
- At least 2 growth hypotheses required (budget: min_growth=2, max_new=2)

## Research Phase (2026-05-07 — Build)

- **CEO Verdict**: PROCEED
- Research grounded in live system observation
- Two-tier detection strategy confirmed (fast path + child process verification)
- Minimal tech stack: subprocess + rich (no libtmux)
- Architecture: discover -> analyze -> display pipeline

## Source Notes

### Build Phase
- [tmux Session Discovery](sources/tmux-session-discovery.md) — Two-tier detection strategy for finding Claude Code and OpenCode in tmux panes
- [Pane Content Capture](sources/pane-content-capture.md) — tmux capture-pane approach, ~5-10ms per pane
- [Claude Code Terminal Patterns](sources/claude-code-terminal-patterns.md) — Markers for idle/working/needs-input states
- [OpenCode Terminal Patterns](sources/opencode-terminal-patterns.md) — Bubble Tea TUI markers for state detection
- [Tech Stack Recommendation](sources/tech-stack-recommendation.md) — subprocess + rich, architecture pattern and data model
- [Similar Projects](sources/similar-projects.md) — No direct equivalent found, novel tool

### Improve Cycle
- [pytest-cov for src Layout](sources/pytest-cov-src-layout.md) — Coverage configuration, source_pkgs key, fail_under threshold
- [mypy Strict Mode](sources/mypy-strict-src-layout.md) — warn_unreachable, packages key, test overrides, subprocess.run gotchas
- [CLI Expansion (Subcommands)](sources/cli-expansion-subcommands.md) — argparse subparsers, backward compat, filtering/sorting flags
- [Watch Mode (Rich Live)](sources/watch-mode-rich-live.md) — Flicker-free refresh, no threading needed, ~50ms poll cycle
- [One-Line Summary & Notifications](sources/oneline-summary-and-notifications.md) — tmux status bar integration, macOS osascript notifications

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
- [Improve Cycle Research (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-improve-research.md) — Research findings, CEO PROCEED, 5 focus areas
- [H1 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-h1-complete.md) — mypy fix delivered, score 0.517 → 1.0, first improve experiment
- [H2 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-h2-complete.md) — pytest-cov configured, 98% coverage, second improve experiment
- [H4 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-h4-complete.md) — Observability expanded, scan_id tracing, all 4 improve hypotheses complete
- [Cycle 1 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle1-complete.md) — Full cycle summary, 12 experiments total, 80% keep rate

## Experiment History

### Build Phase (Experiments 001-007)
- [Experiment #001](experiments/cc-monitoring-agent-001.md) — Project scaffold + eval harness (**KEEP**, +1.0)
- [Experiment #002](experiments/cc-monitoring-agent-002.md) — Data model + tmux pane discovery (**KEEP**, +0.0)
- [Experiment #003](experiments/cc-monitoring-agent-003.md) — Pane capture + state detection (**KEEP**, +0.0)
- [Experiment #004](experiments/cc-monitoring-agent-004.md) — Activity summarization (**KEEP**, +0.0)
- [Experiment #005](experiments/cc-monitoring-agent-005.md) — Rich table display + CLI wiring (**KEEP**, +0.0)
- [Experiment #006](experiments/cc-monitoring-agent-006.md) — Structured logging with loguru (**KEEP**, +0.0)
- [Experiment #007](experiments/cc-monitoring-agent-007.md) — Integration tests + validation (**KEEP**, +0.0)

### Improve Cycle 1 (Experiments 008-011 + 1 revert)
- [Experiment #008](experiments/cc-monitoring-agent-008.md) — Fix mypy strict-mode type errors (**KEEP**, H1)
- [Experiment Revert](experiments/cc-monitoring-agent-revert-002.md) — Configure pytest-cov (**REVERT**, scope violation)
- [Experiment #009](experiments/cc-monitoring-agent-009.md) — Configure pytest-cov retry (**KEEP**, H2, 98% coverage)
- [Experiment #010](experiments/cc-monitoring-agent-010.md) — Watch mode with Rich Live (**KEEP**, H3, 81 tests)
- [Experiment #011](experiments/cc-monitoring-agent-011.md) — Observability expansion (**KEEP**, H4, scan_id tracing)
