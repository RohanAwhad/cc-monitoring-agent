---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Improve Cycle 3)

## CEO Verdict: PROCEED

**Rationale:** Strategy correctly identifies H1 (eval blocker + PR merges) as the critical prerequisite. All 3 unique backlog items are addressed (H2-H4). Growth dimension requirement met (4 hypotheses tagged). New item cap respected (2/2). FEEC ordering correct: FIX first, then EXPLOIT.

## Context

- **Current composite score:** 0.539
- **Weakest dimensions:** type_check (0.4), capability_surface (0.31), observability (0.5)
- **Cycle 2 result:** 0/3 kept — all reverted due to systemic eval blocker (mypy can't resolve src-layout imports with system Python)
- **Root cause identified:** `mypy_path = "src"` missing from pyproject.toml
- **Unmerged PRs:** 4 open PRs (#2, #5, #7, #9) with correct, reviewed code sitting on branches

## Hypotheses (5)

### H1: Fix eval blocker and merge 4 open PRs (FIX, high priority)
- Add `mypy_path = "src"` to pyproject.toml
- Merge PRs in dependency order: #2 → #5 → #7 → #9
- **Expected impact:** type_check 0.4→1.0, tests 0.5→1.0, coverage 0.5→1.0, observability 0.5→0.7, capability_surface 0.31→0.4+
- **Critical:** All other hypotheses depend on this

### H2: Filtering and sorting flags (EXPLOIT, high priority)
- Add `--state`, `--agent`, `--sort` flags to status subcommand
- **Expected impact:** capability_surface +0.05

### H3: One-line summary mode (EXPLOIT, high priority)
- Add `ccm summary` subcommand for tmux status bar integration
- **Expected impact:** capability_surface +0.04

### H4: State change notifications (EXPLOIT, medium priority)
- Add `--notify` flag to watch subcommand
- Use `terminal-notifier` as primary, `osascript` as fallback (Sequoia issue)
- **Expected impact:** capability_surface +0.05

### H5: Boost observability (EXPLOIT, medium priority)
- Request ID tracing via contextvars, remaining function coverage
- **Expected impact:** observability 0.5→0.8+

## Execution Order
1. H1 first (prerequisite for all others)
2. H2-H4 can be parallelized after H1
3. H5 last (check what PR #9 already contributes)

## CEO Instructions
- Execute H1 FIRST — use `gh pr merge`, don't reimplement
- Verify eval composite improved before proceeding to H2-H5
- H5 should check what PR #9 already contributes after merge

## Anti-patterns
- Don't skip H1 — root cause of all cycle 2 failures
- Don't branch from experiment branches — branch from main after H1
- Don't use bare osascript for notifications (Sequoia silent fail)
- Don't add click/typer — argparse subcommands sufficient
