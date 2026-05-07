## Strategy — 2026-05-07 (Improve Cycle 3)

### Observations
- **Current composite score:** 0.539
- **Weakest eval dimensions:** type_check (0.4, 12 errors), capability_surface (0.31, surface=44/140), observability (0.5, 33% fn coverage)
- **Tests/coverage:** Both 0.5 — "not detected" despite 81 tests and 98% coverage existing on experiment branches
- **Healthy dimensions:** lint (1.0), guard_patterns (1.0), config_parser (1.0)
- **Last 3 experiments:** exp 4 watch mode (KEEP), exp 5 observability (KEEP), exp 8 notifications (REVERT)
- **Experiment history:** 4 kept, 2 reverted across 6 experiments. Both reverts caused by systemic eval blocker, not bad code.
- **Pattern — infrastructure blocker:** Factory eval runs `python -m mypy` with system Python which cannot resolve src-layout imports. This caused ALL cycle 2 reverts. Researcher confirmed `mypy_path = "src"` in pyproject.toml as fix.
- **Pattern — unmerged PRs:** 4 open PRs (#2 mypy fix, #5 pytest-cov, #7 watch mode, #9 observability) contain correct, reviewed code but are NOT merged to main. All 3 backlog items depend on PR #7's subcommand architecture.
- **Backlog dedup:** 6 items listed but only 3 unique (formatting variants). Unique items: filtering/sorting, summary mode, notifications.
- **CEO priorities:** (1) Fix eval blocker + merge PRs, (2) Clear backlog, (3) At least 2 growth hypotheses.

### Design Space
| Dimension | Score | Notes |
|---|---|---|
| Features | 4 | Full discover→analyze→display pipeline, watch mode on branch |
| Bug fixes | 2 | mypy fix done (PR #2) but not merged; eval blocker persists |
| Instrumentation | 3 | loguru + scan_id tracing on branch (PR #9), not merged |
| Flow changes | 2 | Subcommand refactor on branch (PR #7), not merged |
| New agents | 0 | N/A |
| Prompt engineering | 0 | N/A |
| Eval improvements | 1 | Basic pass/fail score.py exists |
| Knowledge management | 4 | 7+ experiments archived with source notes |
| Infrastructure | 1 | No CI, pytest-cov on branch not merged, eval blocked |
| Operational execution | 2 | CLI runs, smoke test passes |
| Self-evolution | 0 | N/A |

**Underserved:** Infrastructure (eval blocker), Bug fixes (unmerged PRs), Operational execution

### Hypotheses

#### H1: Fix eval blocker and merge 4 open PRs to main
- **Category:** FIX
- **Type:** operational
- **New:**
- **What:** Two-step fix: (1) Add `mypy_path = "src"` to `[tool.mypy]` in pyproject.toml on main — 1-line config change that tells mypy where to find packages when running from system Python. (2) Merge the 4 open PRs (#2, #5, #7, #9) to main in dependency order: #2 (mypy fix) → #5 (pytest-cov) → #7 (watch mode/subcommands) → #9 (observability). Resolve merge conflicts at each step.
- **Execution step:** (1) On main, add `mypy_path = "src"` under `[tool.mypy]` in pyproject.toml, commit. (2) Verify `python -m mypy src/` passes with system Python. (3) Merge PRs in order: `gh pr merge 2 --merge`, `gh pr merge 5 --merge`, `gh pr merge 7 --merge`, `gh pr merge 9 --merge` — resolve conflicts between each. (4) Run `python eval/score.py` to confirm composite score improvement.
- **Expected output:** All 4 PRs merged to main. `python -m mypy src/` exits 0 with system Python. Eval composite increases substantially (type_check, tests, coverage, observability, capability_surface all improve).
- **Why:** Root cause of all cycle 2 failures. Researcher confirmed the fix. Until PRs are merged, main is stuck at cycle 0 state while correct work sits on branches. This single hypothesis unblocks every backlog item.
- **Expected impact:** type_check 0.4→1.0, tests 0.5→1.0, coverage 0.5→1.0, observability 0.5→0.7, capability_surface 0.31→0.4+
- **Priority:** high

#### H2: Add filtering and sorting flags to status subcommand
- **Category:** EXPLOIT
- **Growth dimension:** capability_surface
- **Backlog item:** Add filtering and sorting flags (--state, --agent, --sort) to status subcommand for usability with many sessions
- **What:** Add three CLI flags to the `status` subparser (available after H1 merges PR #7): `--state` (filter by working/idle/needs_input), `--agent` (filter by claude/opencode), `--sort` (sort by state/agent/tmux_target, default: state). Filter `list[AgentSession]` before display, sort with `sorted()` on chosen field. Add tests for each flag and combinations.
- **Why:** Correctly implemented in cycle 2 but reverted due to eval blocker (now fixed by H1). Code pattern is validated. Researcher confirmed Rich `Live` + pre-filter approach is simpler than interactive TUI. Adds public functions and entry points.
- **Expected impact:** capability_surface +0.05 (new public functions + flag handling)
- **Priority:** high

#### H3: Add one-line summary mode (ccm summary)
- **Category:** EXPLOIT
- **Growth dimension:** capability_surface
- **Backlog item:** Add one-line summary mode (ccm summary or --oneline) for tmux status bar and shell prompt integration
- **What:** Add `summary` subcommand to `cli.py` via existing subparser infrastructure (from PR #7). Output format: `3 agents: 2 working, 1 idle` — plain text, no ANSI codes, no trailing newline. Enables `set -g status-right '#(ccm summary)'` in tmux.conf. Add tests for output format with various session counts.
- **Why:** Correctly implemented in cycle 2, reverted by eval blocker. Researcher confirmed output format. New subcommand entry point + summary function grow capability_surface.
- **Expected impact:** capability_surface +0.04 (new subcommand + summary function)
- **Priority:** high

#### H4: Add state change notifications (ccm watch --notify)
- **Category:** EXPLOIT
- **Growth dimension:** capability_surface
- **Backlog item:** Add state change notifications (ccm watch --notify) — macOS osascript notification on needs_input transitions
- **What:** Add `--notify` flag to the `watch` subparser. Track previous scan state, compare with current; when any session transitions to `needs_input`, fire macOS notification. Use `terminal-notifier` as primary (check via `shutil.which`), fall back to `osascript` with stderr warning about Sequoia permissions. Add tests for state diff detection and notification dispatch (mocked).
- **Why:** Final backlog item. Researcher identified critical macOS Sequoia issue — `osascript` silently fails without notification permissions. `terminal-notifier` fallback is essential. Adds notification module, public functions, flag handling.
- **Expected impact:** capability_surface +0.05 (notification module + functions), experiment_diversity +0.05 (new category)
- **Priority:** medium

#### H5: Boost observability — request tracing and remaining function coverage
- **Category:** EXPLOIT
- **Growth dimension:** observability
- **New:**
- **What:** After H1 merges PR #9's observability work to main, fill remaining gaps: (1) Add request ID tracing via `contextvars` — generate unique scan_id at CLI entry, propagate through discover→analyze→display so all log lines correlate. (2) Add debug logging to remaining uninstrumented functions (target: 80%+ function coverage). (3) Ensure loguru file sink uses `serialize=True` for structured JSON output detectable by factory eval.
- **Why:** Observability at 0.5 on main. PR #9 adds some coverage but may not reach 80%+. Factory eval checks function_coverage and structured_logging — getting both above threshold moves score to 0.8+.
- **Expected impact:** observability 0.5→0.8+ (function coverage 33%→80%+, structured_logging=True, request tracing)
- **Priority:** medium

### Anti-patterns to Avoid
- **Don't skip H1.** All cycle 2 reverts were caused by the eval blocker. Without `mypy_path = "src"` and merged PRs, H2-H5 will fail the same way.
- **Don't branch from experiment branches.** Cycle 2 branched from PR #7's branch — caused merge issues. After H1, all work branches from main.
- **Don't use libtmux** — subprocess is sufficient (build phase validated).
- **Don't add click/typer** — argparse subcommands enough for 4 commands.
- **Don't use bare `osascript` for notifications** — silently fails on macOS Sequoia. Use `terminal-notifier` with `osascript` fallback.
- **Don't repeat `detect_state` str vs Literal mismatch** — ensure return types are exact Literal types.
- **Don't implement interactive TUI filtering** — CLI flags + pipes are simpler and more composable.
