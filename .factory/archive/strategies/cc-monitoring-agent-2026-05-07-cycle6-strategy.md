---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 6)

## Context

- **Current composite score:** 1.0 (all 5 eval dimensions at 1.0)
- **Project eval:** tests=1.0 (81 passed, 97% coverage), typecheck=1.0, lint=1.0, cli_runs=1.0, formatting=1.0
- **Prior cycle (5):** 3/3 KEPT — breakthrough after 10 consecutive reverts in cycles 3-4
- **Backlog:** EMPTY — all 3 original items (filtering, summary, notifications) delivered in cycle 5
- **Competitive landscape:** 12+ competitors identified across hook-based, TUI, and OTel categories
- **Total experiments to date:** 26 (14 kept, 12 reverted)

## CEO Verdict

**PROCEED** — Two well-scoped growth hypotheses targeting capability_surface. Both follow the validated no-new-files pattern. Both are pure additions — no regression risk to eval 1.0.

## Approved Hypotheses (Priority Order)

### H1: `ccm attach` subcommand for quick-jump navigation
- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **Implementation:** Add `_run_attach(args)` handler in `cli.py`. Support fuzzy matching: `ccm attach claude` jumps to first Claude session, `ccm attach 0:1.2` jumps to exact target. If multiple matches, print a numbered list and exit.
- **Effort:** ~20 lines of logic in `cli.py`, no new files
- **Tests:** 5+ tests for exact match, partial match, no match, and multiple matches
- **Expected impact:** capability_surface +0.05, experiment_diversity +0.03
- **Rationale:** Every competitor (TmuxCC, ATM, Workmux) offers quick-jump. Researcher ranked this #1 by value/effort ratio. CEO confirmed it as highest-value quick win.

### H2: Token/cost estimation via `--costs` flag
- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **Implementation:** Add `--costs` flag to `status` subparser in `cli.py`. Add `estimate_session_cost(session: AgentSession) -> dict[str, int] | None` to `analyzer.py`. Read Claude Code's local JSONL conversation files (`~/.claude/projects/*/conversations/*.jsonl`) to extract token usage. Display cost column in Rich table when `--costs` is passed.
- **Effort:** Moderate — two existing files modified
- **Tests:** 6+ tests with mocked conversation files
- **Expected impact:** capability_surface +0.08, research_grounding +0.03
- **Rationale:** CEO identified this as biggest differentiator — getting hook-level data (token/cost) without hooks, just by reading local files. No other pane-scraping tool does this.

## Anti-Patterns to Avoid
1. **Don't create new files** — validated in cycles 4-5
2. **Don't introduce new dependencies** — keep stdlib + existing deps (rich, loguru)
3. **Don't break existing subcommand structure** — run ruff format after changes
4. **Don't over-scope** — one focused feature per hypothesis
5. **Don't add try/except** — use early return for graceful degradation

## Builder Instructions
- Follow no-new-files pattern: add functions to existing modules only
- Run `ruff format` and `ruff check` before committing
- Run `uv run mypy src/ --strict` to verify type safety
- Each hypothesis is a separate experiment branch
- Do NOT modify eval/score.py or .factory/
