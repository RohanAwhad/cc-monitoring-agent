---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 3 Research Complete)

## Context

Cycle 3 research completed. CEO verdict: PROCEED. Project composite 0.539, project eval 1.0. 4 open PRs from cycle 1 (#2, #5, #7, #9) unmerged. All 3 cycle 2 experiments reverted due to systemic eval blocker.

## Key Research Outcomes

1. **Eval blocker root cause identified** with project-level fix: `mypy_path = "src"` in `[tool.mypy]` section of pyproject.toml. This tells system Python's mypy where to find packages in src-layout projects.

2. **Competitive landscape matured**: claude-tmux is now the main competitor, using active hooks (SQLite + plugin integration) vs ccm's passive pane scraping. ccm's differentiator is zero-config, works with any agent.

3. **macOS Sequoia breaks osascript notifications**: `terminal-notifier` is the reliable alternative. This affects the `--notify` backlog item.

4. **TUI architecture validated**: Rich `Live` + CLI flags is the right approach. Textual would add dependency weight for marginal interactive benefit.

## CEO Priorities for Strategist

1. FIX: Merge 4 open PRs (#2, #5, #7, #9) to main
2. FIX: Add `mypy_path = "src"` to unblock factory eval
3. EXPLOIT: Re-apply 3 reverted backlog items (filtering, summary, notifications)
4. Growth dimensions must be targeted (capability_surface)
5. Deduplicate backlog: 3 unique items, not 6

## Score State

- Factory composite: 0.539
- Project eval: 1.0
- Build phase: 7/7 complete
- Cycle 1: 4/5 kept (80%)
- Cycle 2: 0/3 kept (0% — systemic eval blocker)
- Total experiments: 15 (11 kept, 4 reverted)
