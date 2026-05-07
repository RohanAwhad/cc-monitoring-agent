---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Improve Cycle Research)

## Context

Build phase complete (7/7 phases, 70 tests, 7 experiments all kept). Project entered improve mode. Researcher conducted external research on growth opportunities. CEO reviewed and issued PROCEED verdict.

## Score State

- Researcher reported composite 1.0 (possibly stale eval)
- CEO observed 0.517 on fresh eval: type_check=0.4 (12 mypy errors), capability_surface=0.31, observability=50%
- Discrepancy flagged — fresh eval will be run during experiments

## Research Findings (5 Focus Areas, FEEC Order)

### 1. FIX: pytest-cov + coverage configuration
- Add `pytest-cov` dev dep, configure `source_pkgs`, `fail_under=80`
- Makes test quality measurable beyond pass/fail

### 2. EXPLOIT: Watch mode (`ccm watch`)
- Highest-impact feature — continuous observation is the core monitoring UX
- Rich `Live` context manager for flicker-free refresh
- No threading needed (~50ms discover+analyze cycle)
- Requires migrating CLI to subcommands (argparse subparsers)
- **Growth dimension: capability_surface**

### 3. EXPLOIT: Filtering and sorting flags
- `--state`, `--agent`, `--sort` flags on status subcommand
- Pure Python filtering on `list[AgentSession]`
- **Growth dimension: capability_surface**

### 4. EXPLORE: One-line summary mode
- `ccm summary` for tmux status bar / shell prompt integration
- Output: `3 agents: 2 working, 1 idle` compact format
- **Growth dimension: capability_surface**

### 5. EXPLORE: State change notifications
- `ccm watch --notify` triggers macOS notification on `needs_input` transitions
- macOS `osascript` — no extra deps
- **Growth dimension: capability_surface**

## CEO Priorities for Strategist

1. FIX type_check (12 mypy errors, score 0.4) — highest priority
2. EXPLOIT watch mode — highest growth impact on capability_surface
3. At least 2 growth hypotheses required (budget: min_growth=2, max_new=2)
4. Backlog item is a placeholder — can be cleared

## Hypothesis Budget

- **Backlog items**: 1 (placeholder, clearable)
- **Max new items**: 2
- **Min growth hypotheses**: 2
