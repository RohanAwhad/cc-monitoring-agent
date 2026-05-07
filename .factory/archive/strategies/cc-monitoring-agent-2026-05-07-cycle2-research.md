---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Improve Cycle 2 Research)

## Context

Improve cycle 2 research phase. Project eval score is 1.0 (all 5 dimensions pass: tests, typecheck, lint, cli_runs, formatting). Factory composite was stale at 0.517 from cycle 1 — actual project state is fully passing.

## CEO Verdict on Research

**PROCEED** — Research comprehensive (172 lines), covers all key areas. Agent timed out but report was complete.

## Key Findings

1. **Score reality**: All eval dimensions pass. The 0.517 composite was stale from cycle 1's `last_eval.json`. No FIX hypotheses needed for eval dimensions.
2. **4 open PRs from cycle 1 not merged**: H1 (mypy fix), H2 (pytest-cov), H3 (watch mode), H4 (observability) — these features are NOT on main yet.
3. **Backlog**: 3 unique items remain (duplicated to 6 lines in backlog.md):
   - Filtering and sorting flags (`--state`, `--agent`, `--sort`)
   - One-line summary mode (`ccm summary` / `--oneline`)
   - State change notifications (`ccm watch --notify`)
4. **No new external sources needed** — cycle 1 research already covers pytest-cov, mypy, CLI expansion, Rich Live, summary mode, and notifications.
5. **Biggest growth opportunity**: capability_surface (0.31 in factory eval) — all 3 backlog items target this dimension.

## CEO Priorities for Strategist

- Focus on the 3 backlog items (filtering/sorting, one-line summary, notifications) plus any new growth items
- type_check (0.4) and tests/coverage (0.5) won't improve until cycle 1 PRs are merged
- capability_surface (0.31) is the biggest growth opportunity

## Research Areas Covered (with existing source notes)

| Topic | Source Note | Status |
|---|---|---|
| pytest-cov for src layout | `sources/pytest-cov-src-layout.md` | Already archived (cycle 1) |
| mypy strict mode | `sources/mypy-strict-src-layout.md` | Already archived (cycle 1) |
| CLI subcommands | `sources/cli-expansion-subcommands.md` | Already archived (cycle 1) |
| Watch mode (Rich Live) | `sources/watch-mode-rich-live.md` | Already archived (cycle 1) |
| One-line summary + notifications | `sources/oneline-summary-and-notifications.md` | Already archived (cycle 1) |
