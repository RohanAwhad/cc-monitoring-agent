## Strategy — 2026-05-07 (Improve Cycle 6)

### Observations
- **Current composite score:** 1.0 (perfect — all 5 eval dimensions at 1.0)
- **Project eval:** tests=1.0 (81 passed, 97% coverage), typecheck=1.0, lint=1.0, cli_runs=1.0, formatting=1.0
- **Last 3 experiments:** exp 18 filtering/sorting (KEEP), exp 19 summary subcommand (KEEP), exp 20 desktop alerts (KEEP)
- **Overall history:** 20 experiments, 8 kept, 12 reverted. Keep rate improved from 38% to ~60% in recent cycles after infrastructure fixes.
- **Pattern — cycles 4-5 success:** The no-new-files strategy (add functions to existing modules) was validated. All 3 backlog items cleared in cycle 5 with 100% keep rate.
- **Pattern — eval 1.0 is fragile:** Many reverts (exp 8, 10, 11, 14, 15, 16, 17) were caused by tiny score regressions (-0.001 to -0.032). Any new code must pass all checks cleanly.
- **Backlog:** EMPTY. All 3 original items (filtering, summary, notifications) delivered. 13 GitHub issues exist but are all factory-created experiment issues (already delivered).
- **Competitive landscape shift:** 10+ new competitors identified (ATM, TmuxCC, Agent Deck, OTel-based tools). ccm's differentiator is zero-config + agent-agnostic, but gaps exist in: quick-jump navigation, cost/token tracking, multi-agent support.
- **CEO priorities:** (1) capability_surface via new features, (2) `ccm attach` as highest-value quick win, (3) token/cost estimation as differentiator, (4) no new files, (5) maintain eval 1.0.

### Design Space
| Dimension | Score | Notes |
|---|---|---|
| Features | 5 | Full pipeline + watch + filtering + summary + notifications |
| Bug fixes | 4 | All known bugs fixed, eval stable at 1.0 |
| Instrumentation | 4 | loguru + scan_id tracing + structured JSON + 97% coverage |
| Flow changes | 3 | Subcommand architecture, filter/sort pipeline |
| New agents | 1 | Only Claude + OpenCode detected |
| Prompt engineering | 0 | N/A for CLI tool |
| Eval improvements | 2 | Basic score.py, no project-specific eval dimensions |
| Knowledge management | 4 | 20 experiments archived with patterns |
| Infrastructure | 3 | pytest-cov, mypy strict, ruff — no CI/CD |
| Operational execution | 4 | CLI runs, smoke test, watch mode, notifications |
| Self-evolution | 0 | N/A |

**Underserved:** New agents (1), Eval improvements (2), Flow changes (3)

### Hypotheses

#### H1: Add `ccm attach` subcommand for quick-jump navigation
- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **New:**
- **What:** Add `attach` subcommand to `cli.py` that takes a tmux target (or partial match on session name/agent type) and runs `tmux select-window -t` + `tmux select-pane -t` to jump directly to that agent's pane. Add `_run_attach(args)` handler in `cli.py`. Support fuzzy matching: `ccm attach claude` jumps to first Claude session, `ccm attach 0:1.2` jumps to exact target. If multiple matches, print a numbered list and exit. Add 5+ tests for exact match, partial match, no match, and multiple matches.
- **Why:** Every competitor (TmuxCC, ATM, Workmux) offers quick-jump. Researcher ranked this #1 by value/effort ratio. CEO confirmed it as highest-value quick win. ~20 lines of logic in `cli.py`, no new files needed.
- **Expected impact:** capability_surface +0.05 (new subcommand + public function), experiment_diversity +0.03 (new feature category). Eval 1.0 maintained — pure addition, no regressions.
- **Priority:** high

#### H2: Add token/cost estimation from Claude Code conversation files
- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **New:**
- **What:** Add `--costs` flag to the `status` subparser in `cli.py`. When enabled, read Claude Code's local JSONL conversation files (`~/.claude/projects/*/conversations/*.jsonl`) to extract token usage per session. Add `estimate_session_cost(session: AgentSession) -> dict[str, int] | None` to `analyzer.py` that finds the most recent conversation file matching the session's working directory, parses token counts from the JSONL entries, and returns `{"input_tokens": N, "output_tokens": N, "estimated_cost_usd": float}`. Display cost column in the Rich table when `--costs` is passed. Add 6+ tests with mocked conversation files.
- **Why:** CEO identified this as the biggest differentiator — getting hook-level data (token/cost) without hooks, just by reading local files. No other pane-scraping tool does this. Closes the largest gap vs ATM and OTel-based competitors. Researcher ranked it Tier 2 but highest value.
- **Expected impact:** capability_surface +0.08 (new flag + cost estimation function + display column), research_grounding +0.03 (implements technique from competitive research). Eval 1.0 maintained.
- **Priority:** high

### Anti-patterns to Avoid
- **Don't create new files.** Validated in cycles 4-5: adding functions to existing modules avoids factory eval module-count regressions that caused experiments 10, 11, 14 to revert.
- **Don't introduce new dependencies without justification.** The `anthropic` dep addition in exp 17 contributed to scope concerns. Keep stdlib + existing deps (rich, loguru).
- **Don't break existing subcommand structure.** Experiments 10-11 failed partly due to lint/formatting regressions in modified CLI code. Run ruff format after changes.
- **Don't over-scope.** Experiments that bundled multiple features (exp 14: filtering + observability) tended to revert. Keep each hypothesis to one focused feature.
- **Don't add try/except.** Per user CLAUDE.md, let exceptions surface. Graceful degradation for cost estimation (return None if no conversation files found) should use early return, not exception catching.
