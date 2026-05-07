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

- **State**: improve (build complete, cycle 1 complete, cycle 2 complete — blocked, cycle 3 complete — blocked)
- **Current Score**: 0.537 (factory composite) / 1.0 (project eval)
- **Experiments Run**: 20 total (7 build + 5 improve cycle 1 + 3 improve cycle 2 + 5 improve cycle 3), 8 reverted, 1 error
- **Kept**: 11, **Reverted**: 8, **Error**: 1
- **Total Tests**: 81, **Coverage**: 97%
- **Build Phases**: 7/7 complete
- **Improve Cycle 1**: Complete — 4 hypotheses delivered (H1-H4), 5 experiments (4 kept, 1 reverted), keep rate 80%
- **Improve Cycle 2**: Complete — 3 hypotheses attempted, ALL 3 REVERTED due to systemic eval issue, keep rate 0%
- **Improve Cycle 3**: Complete — 5 experiments (1 kept, 3 reverted, 1 error), keep rate 20%
  - H1 (KEEP): mypy_path fix + 4 PR merge — operational prerequisite
  - H2 (REVERT): Filtering/sorting — score regression -0.018
  - H2 retry (REVERT): Filtering/sorting — anti_pattern + score noise -0.001
  - H3 (ERROR): Summary mode — dirty factory files in PR
  - H3 retry (REVERT): Summary mode — threshold 0.800 mathematically unachievable (max possible ~0.645)
- **Systemic blocker**: Factory eval threshold (0.800) is unachievable — tests/coverage/research_grounding overlay dimensions cap max score at ~0.645

## Score History

- **Build phase**: Internal eval 1.0, factory composite 0.517 (discrepancy due to stale eval cache)
- **Cycle 1 H1 (mypy fix)**: Factory 0.517 → 0.517 — type_check dimension fixed (12 errors → 0)
- **Cycle 1 H2 (pytest-cov)**: Factory 0.517 → 0.517 — 98% coverage achieved
- **Cycle 1 H3 (watch mode)**: Factory 0.517 → 0.517 — ccm watch subcommand added, 81 total tests
- **Cycle 1 H4 (observability)**: Factory 0.517 → 0.517 — scan_id tracing, structured JSON logs
- **Post cycle 1 merge**: Factory composite 0.539 (main branch, after merging cycle 1 PRs)
- **Cycle 2 H1 (filtering/sorting)**: Factory 0.539 → REVERT (delta -0.058, systemic eval failure)
- **Cycle 2 H2 (one-line summary)**: Factory 0.539 → REVERT (delta -0.049, systemic eval failure)
- **Cycle 2 H3 (notifications)**: Factory 0.539 → REVERT (delta -0.032, systemic eval failure)
- **Cycle 3 H1 (eval blocker + PR merge)**: Factory 0.539 → 0.537 — operational experiment, mypy_path fix + 4 PRs merged, project eval 1.0
- **Cycle 3 H2 (filtering/sorting)**: Factory 0.537 → REVERT (delta -0.018, type_check regression)
- **Cycle 3 H2 retry (filtering/sorting)**: Factory 0.537 → REVERT (delta -0.001, anti_pattern + noise)
- **Cycle 3 H3 (summary mode)**: ERROR — PR included dirty factory files
- **Cycle 3 H3 retry (summary mode)**: Factory 0.572 → REVERT (threshold 0.800 unachievable, max possible ~0.645)

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

## Improve Cycle 2 Summary (2026-05-07)

| Hypothesis | Category | Target Dimension | Verdict | Score Delta | Key Result |
|---|---|---|---|---|---|
| H1: Filtering/sorting flags | EXPLOIT | capability_surface | **REVERT** | -0.058 | Systemic eval failure — code correct, tests pass |
| H2: One-line summary mode | EXPLORE | capability_surface | **REVERT** | -0.049 | Systemic eval failure — code correct, tests pass |
| H3: State change notifications | EXPLORE | capability_surface | **REVERT** | -0.032 | Systemic eval failure — code correct, tests pass |

**Keep rate**: 0% (0/3)
**Root cause**: Factory eval runs mypy/lint overlay dimensions using system Python, which cannot resolve project imports in src-layout (`src/cc_monitor/`). Every new Python file amplifies unresolvable imports, causing score regression. All 3 implementations were functionally correct (e2e pass, project eval 1.0).
**Conclusion**: Further improve cycles on this project are blocked until the factory eval infrastructure is fixed to use `uv run` or project venvs for overlay dimensions.

## Improve Cycle 3 Summary (2026-05-07)

| Experiment | Hypothesis | Category | Verdict | Score Delta | Key Result |
|---|---|---|---|---|---|
| #015 (ID 9) | Fix eval blocker + merge 4 PRs | FIX | **KEEP** | -0.002 | mypy_path fix, 4 PRs merged, project eval 1.0 |
| #016 (ID 10) | Filtering/sorting flags | EXPLOIT | **REVERT** | -0.018 | Score regression from type_check overlay |
| #017 (ID 11) | Filtering/sorting retry | EXPLOIT | **REVERT** | -0.001 | Anti-pattern blocked + score noise |
| #018 (ID 12) | Summary mode | EXPLOIT | **ERROR** | 0.0 | PR included dirty .factory/ files |
| #019 (ID 13) | Summary mode retry | EXPLOIT | **REVERT** | 0.0 | Threshold 0.800 unachievable (max ~0.645) |

**Keep rate**: 20% (1/5) — only the operational H1 was kept
**Post-H1 keep rate**: 0% (0/4) — all code-adding experiments blocked
**Root cause**: Factory eval threshold (0.800) is mathematically unachievable. Three overlay dimensions are broken:
- `tests`: 0.5 (factory can't detect pytest suite)
- `coverage`: 0.5 (factory can't detect coverage config)
- `research_grounding`: 0.0 (dimension not scored)

These three dimensions alone cap the maximum composite at ~0.645, making the 0.800 precheck threshold impossible to reach regardless of code quality.

**Conclusion**: cc-monitoring-agent is functionally complete (project eval 1.0, 81 tests, 97% coverage, mypy clean) but cannot improve its factory composite without infrastructure changes to the eval system.

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
3. **EXPLOIT**: Filtering and sorting flags (`--state`, `--agent`, `--sort`) ❌ (Cycle 2+3, reverted — eval systemic)
4. **EXPLORE**: One-line summary mode for tmux/shell prompt integration ❌ (Cycle 2+3, reverted — eval systemic)
5. **EXPLORE**: State change notifications via macOS osascript ❌ (Cycle 2, reverted — eval systemic)

### CEO Priorities for Strategist

- FIX type_check (12 mypy errors, score 0.4) ✅ (H1)
- EXPLOIT watch mode — highest growth impact on capability_surface ✅ (H3)
- At least 2 growth hypotheses required (budget: min_growth=2, max_new=2)

## Improve Cycle 3 — Research Findings (2026-05-07)

CEO Verdict: **PROCEED**. Research thorough and actionable.

### Key Findings

1. **Eval blocker fix identified**: `mypy_path = "src"` in pyproject.toml — project-level workaround for system Python mypy resolution
2. **Competitive landscape shift**: claude-tmux (v1.2.0) is now a full-featured competitor using active hooks; ccm differentiates via passive zero-config pane scraping
3. **macOS Sequoia notification issue**: osascript silently fails without permissions; `terminal-notifier` is the reliable alternative
4. **TUI decision validated**: Rich `Live` + CLI flags preferred over Textual `DataTable` — simpler, no new dependency
5. **CLI pattern confirmed**: argparse subparsers sufficient for ccm's 4-subcommand ceiling

### CEO Priorities for Strategist

1. FIX: Merge 4 open PRs (#2, #5, #7, #9) to main — prerequisite for all backlog items
2. FIX: Add `mypy_path = "src"` to pyproject.toml to unblock factory eval
3. EXPLOIT: Clear backlog items (filtering, summary, notifications) — all 3 were correctly implemented before, just eval-blocked
4. Growth dimensions must be targeted (capability_surface via new features)
5. Backlog has 3 unique items (6 listed but 3 are formatting duplicates)

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

### Cycle 3 Research
- [Competitive Landscape (Cycle 3)](sources/competitive-landscape-cycle3.md) — claude-tmux, tmux-orche, pylumbergh — ccm differentiates via passive zero-config scraping
- [Rich Live vs Textual](sources/rich-live-vs-textual-cycle3.md) — Rich `Live` + CLI flags preferred over Textual `DataTable`
- [macOS Notifications (Sequoia)](sources/macos-notifications-sequoia.md) — osascript silent fail, terminal-notifier workaround
- [mypy_path Eval Fix](sources/mypy-path-eval-fix.md) — `mypy_path = "src"` project-level workaround for factory eval blocker
- [CLI Subcommand Patterns (Cycle 3)](sources/cli-subcommand-patterns-cycle3.md) — argparse sufficient for ≤4 subcommands
- [tmux Monitoring Practices (Cycle 3)](sources/tmux-monitoring-practices-cycle3.md) — subprocess + periodic poll validated, libtmux overkill

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
- [Cycle 2 Research (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle2-research.md) — Research complete, all prior sources reused, 3 backlog items identified
- [Cycle 2 Strategy (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle2-strategy.md) — CEO PROCEED, 3 hypotheses targeting capability_surface
- [Cycle 2 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle2-complete.md) — All 3 reverted, systemic eval blocker identified
- [Cycle 3 Research (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle3-research.md) — Research complete, eval blocker fix identified, competitive landscape matured
- [Cycle 3 Strategy (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle3-strategy.md) — CEO PROCEED, 5 hypotheses (FIX eval blocker + 4 EXPLOIT), H1 prerequisite for all
- [Cycle 3 H1 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle3-h1-complete.md) — Eval blocker fixed, 4 PRs merged, project eval 1.0, factory composite 0.537
- [Cycle 3 Complete (2026-05-07)](strategies/cc-monitoring-agent-2026-05-07-cycle3-complete.md) — 5 experiments (1 kept, 3 reverted, 1 error), threshold unachievable

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

### Improve Cycle 2 (Experiments 012-014 — all reverted)
- [Experiment #012](experiments/cc-monitoring-agent-012.md) — Filtering/sorting flags (**REVERT**, -0.058, systemic eval)
- [Experiment #013](experiments/cc-monitoring-agent-013.md) — One-line summary mode (**REVERT**, -0.049, systemic eval)
- [Experiment #014](experiments/cc-monitoring-agent-014.md) — State change notifications (**REVERT**, -0.032, systemic eval)

### Improve Cycle 3 (Experiments 015-019)
- [Experiment #015](experiments/cc-monitoring-agent-015.md) — Fix eval blocker + merge 4 PRs to main (**KEEP**, H1, operational, project eval 1.0)
- [Experiment #016](experiments/cc-monitoring-agent-016.md) — Filtering/sorting flags (**REVERT**, -0.018, type_check overlay)
- [Experiment #017](experiments/cc-monitoring-agent-017.md) — Filtering/sorting retry (**REVERT**, -0.001, anti_pattern + noise)
- [Experiment #018](experiments/cc-monitoring-agent-018.md) — Summary mode (**ERROR**, dirty factory files in PR)
- [Experiment #019](experiments/cc-monitoring-agent-019.md) — Summary mode retry (**REVERT**, threshold unachievable, max ~0.645)
