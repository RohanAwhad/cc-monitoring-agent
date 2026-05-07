## Strategy — 2026-05-07 (Improve Cycle)

### Observations
- **Current composite score:** 0.517
- **Weakest eval dimensions:** type_check (0.4, 12 mypy errors), capability_surface (0.31, surface=44/140)
- **Tests:** 0.5 ("not detected" — factory eval can't find test suite despite 70 tests existing)
- **Coverage:** 0.5 ("no coverage tool detected" — pytest-cov not configured)
- **Healthy dimensions:** lint (1.0), guard_patterns (1.0), config_parser (1.0)
- **Observability:** 0.5 (33% function coverage, structured logging exists but eval reports structured_logging=False, no request tracing)
- **Last experiments:** 7 build experiments (all KEEP), now in first improve cycle. No improve-cycle experiments yet.
- **Backlog:** 1 item — placeholder text ("Missing items requiring human intervention: None identified"). Not actionable — clearing it.
- **CEO priorities:** 1) FIX type_check 12 errors, 2) EXPLOIT watch mode with Rich Live for capability_surface, 3) At least 2 growth hypotheses.
- **Pattern:** Build phase achieved internal eval 1.0 (project's own score.py) but factory composite eval scores 0.517 due to additional dimensions (capability_surface, observability, coverage, etc.) that aren't covered by the project's pass/fail eval. The gap is: project eval passes, but factory wants more surface area, coverage tooling, and type strictness.

### Design Space
| Dimension | Score | Notes |
|---|---|---|
| Features | 4 | Full pipeline: discover → analyze → display, 8 modules |
| Bug fixes | 1 | 12 mypy errors blocking type_check |
| Instrumentation | 2 | loguru added but 33% function coverage, not detected as structured |
| Flow changes | 0 | No refactors attempted |
| New agents | 0 | N/A |
| Prompt engineering | 0 | N/A |
| Eval improvements | 1 | Basic pass/fail score.py exists |
| Knowledge management | 4 | 7 experiments, 6 source notes well-archived |
| Infrastructure | 0 | No CI, no coverage tooling |
| Operational execution | 1 | CLI runs, no live validation documented |
| Self-evolution | 0 | N/A |

**Underserved:** Bug fixes, Instrumentation, Flow changes, Infrastructure

### Hypotheses

#### H1: Fix 12 mypy strict-mode type errors
- **Category:** FIX
- **Backlog item:** Missing items requiring human intervention: None identified.
- **What:** Run `mypy --strict src/cc_monitor/` to identify all 12 errors, then fix each one. Common culprits in this codebase (from build history): `subprocess.run` overloaded type stubs (annotate `result: subprocess.CompletedProcess[str]` explicitly, pass `text=True` as literal not variable), `detect_state` returning `str` instead of `Literal["working", "idle", "needs_input"]`, missing return type annotations. Fix all errors in source files under `src/cc_monitor/`.
- **Why:** type_check is at 0.4 (12 errors, `passed: false`). CEO explicitly flagged this as priority #1. This is the only dimension that currently fails — fixing it unblocks composite score improvement.
- **Expected impact:** type_check 0.4 → 1.0 (+0.03 composite, weight 0.05)
- **Priority:** high

#### H2: Configure pytest-cov and fix test detection
- **Category:** FIX
- **New:**
- **What:** The factory eval reports "no test suite detected" and "no coverage tool detected" despite 70 tests existing. Fix: 1) Add `pytest-cov` to dev dependencies, 2) Add `[tool.coverage.run]` with `source_pkgs = ["cc_monitor"]` to pyproject.toml, 3) Add `[tool.coverage.report]` with `show_missing = true`, `fail_under = 80`, 4) Add `addopts = "--cov=cc_monitor --cov-report=term-missing"` to `[tool.pytest.ini_options]`, 5) Add `packages = ["cc_monitor"]` to `[tool.mypy]` config. Research confirmed `source_pkgs` is essential for src-layout projects.
- **Why:** tests (0.5) and coverage (0.5) each carry significant weight (0.15 + 0.125). Both show "not detected" because the factory eval can't discover pytest or coverage output. Adding pytest-cov with proper config makes both dimensions detectable — potential +0.14 composite gain for a config-only change.
- **Expected impact:** tests 0.5 → 1.0, coverage 0.5 → 1.0, composite +0.14
- **Priority:** high

#### H3: Watch mode with Rich Live (`ccm watch`)
- **Category:** EXPLOIT
- **Growth dimension:** capability_surface
- **New:**
- **What:** Add continuous monitoring via `ccm watch` subcommand. Implementation: 1) Refactor `cli.py` from flat argparse to subcommands via `add_subparsers()` — `ccm status` (current behavior), `ccm watch` (live refresh), bare `ccm` defaults to status for backward compat, 2) Create `src/cc_monitor/watch.py` — watch loop using Rich `Live` context manager for flicker-free terminal refresh, 3) Add `--interval` flag (default 2s), 4) Graceful exit on `KeyboardInterrupt`, 5) Add tests for watch module (mock `time.sleep`, verify `Live.update` called). Uses `set_defaults(func=handler)` dispatch pattern on each subparser.
- **Why:** CEO flagged watch mode as the top growth priority. Continuous observation is the core use case for a monitoring tool. Rich `Live` is already available (rich is a dependency), and discover+analyze takes ~50ms, well within a 2s poll interval. Adds ~15 public functions + 1 module + 1 entry point, significantly growing capability_surface.
- **Expected impact:** capability_surface 0.31 → 0.45+ (new module, subcommand routing, public functions)
- **Priority:** high

#### H4: Expand observability — logging coverage and request tracing
- **Category:** EXPLOIT
- **Growth dimension:** observability
- **What:** 1) Add debug logging to the 12/18 uninstrumented functions across models.py, display.py, cli.py, and __init__.py, 2) Add request-level tracing: generate a unique scan ID (`uuid4().hex[:8]`) at CLI entry in `cli.py`, bind it to loguru context via `logger.bind(scan_id=...)`, propagate through discover → analyze → display so all log lines from a single invocation are correlated, 3) Verify file sink uses structured JSON output (`serialize=True` in loguru config). Files touched: `src/cc_monitor/logging.py`, `src/cc_monitor/cli.py`, `src/cc_monitor/display.py`, `src/cc_monitor/models.py`.
- **Why:** Observability is at 0.5 with 33% function coverage and no request tracing. The factory eval specifically measures function coverage and structured logging detection. Improving to 80%+ function coverage and adding request tracing should move observability from 0.5 to 0.8+.
- **Expected impact:** observability 0.5 → 0.8+ (function coverage 33% → 80%+, request tracing added)
- **Priority:** medium

### Anti-patterns to Avoid
- Don't use libtmux — subprocess confirmed sufficient (build phase validated)
- Don't add click/typer — argparse subcommands are enough for 2-3 commands
- Don't capture scrollback (`-S -`) — visible content only needed
- Don't add LLM-based summarization — heuristic parsing is sufficient
- Don't add daemon mode or persistence — watch mode covers continuous monitoring
- Build phase had repeated issues with `detect_state` returning `str` vs `Literal` — ensure type annotations match exactly when touching state-related code

## New Backlog Items

- Add filtering and sorting flags (`--state`, `--agent`, `--sort`) to status subcommand for usability with many sessions
- Add one-line summary mode (`ccm summary` or `--oneline`) for tmux status bar and shell prompt integration
- Add state change notifications (`ccm watch --notify`) — macOS `osascript` notification on `needs_input` transitions
