## Strategy — 2026-05-07

### Observations
- **Project state:** Research-complete, pre-implementation. No source code exists yet.
- **CEO verdict:** PROCEED — approved two-tier detection, subprocess + rich stack, discover → analyze → display architecture.
- **Eval profile:** 5 dimensions (tests 40%, typecheck 25%, lint 15%, cli_runs 15%, formatting 5%). All currently score 0.
- **No experiment history** — greenfield project.
- **No backlog** — building from scratch.

### Design Space
| Dimension | Score | Notes |
|---|---|---|
| Features | 0 | Nothing implemented |
| Bug fixes | 0 | N/A — no code yet |
| Instrumentation | 0 | No logging |
| Flow changes | 0 | N/A |
| New agents | 0 | N/A |
| Prompt engineering | 0 | N/A |
| Eval improvements | 1 | eval_profile.json and score.py exist |
| Knowledge management | 3 | Research sources well-archived |
| Infrastructure | 0 | No CI, no packaging |
| Operational execution | 0 | Nothing runs yet |
| Self-evolution | 0 | N/A |

**Underserved:** Everything except Knowledge management and Eval improvements.

---

### Hypotheses

#### Phase 1: Project scaffold + eval harness

**GitHub Issue: `feat: project scaffold with pyproject.toml, package structure, and eval harness`**

- **Category:** FIX (nothing works yet — get to green)
- **Growth dimension:** factory_effectiveness
- **What:**
  - Create `pyproject.toml` with project metadata, `rich` dependency, dev deps (`pytest`, `mypy`, `ruff`)
  - Create package structure: `src/cc_monitor/__init__.py`, `src/cc_monitor/__main__.py`, `src/cc_monitor/py.typed`
  - Wire `__main__.py` to print help via argparse (satisfies `cli_runs` eval)
  - Create `tests/__init__.py` and a trivial passing test (satisfies `tests` eval)
  - Ensure `mypy`, `ruff check`, and `ruff format --check` all pass
  - Add `[project.scripts]` entry: `ccm = "cc_monitor.cli:main"`
- **Why:** All 5 eval dimensions must pass before any feature work. Scaffold-first gets the build green.
- **Expected impact:** All eval dimensions → 1.0 (composite 1.0)
- **Priority:** high

---

#### Phase 2: Data model + tmux discovery

**GitHub Issue: `feat: AgentSession data model and tmux pane discovery`**

- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **What:**
  - Create `src/cc_monitor/models.py` — `AgentSession` dataclass with fields: `session_name`, `window_index`, `pane_index`, `agent_type` (Literal["claude", "opencode"]), `state` (Literal["working", "idle", "needs_input"]), `summary`, `pane_pid`, `tmux_target`
  - Create `src/cc_monitor/discovery.py` — `list_all_panes()` calls `tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_command} #{pane_pid}'`, parses output
  - Implement `classify_pane()` — fast path: match `opencode` directly, match `\d+\.\d+\.\d+` for Claude Code candidates
  - Implement `verify_claude_candidate()` — runs `ps -eo pid,ppid,comm`, checks if `pane_pid` has child process named `claude`
  - Implement `discover_sessions()` — orchestrates list → classify → verify, returns `list[AgentSession]` (state/summary left empty at this phase)
  - Add unit tests with mocked subprocess output for discovery logic
- **Why:** Discovery is the foundation — all subsequent features depend on correctly finding agent panes. Two-tier detection (fast path + verify) matches research findings.
- **Expected impact:** capability_surface +0.3, tests remain green
- **Priority:** high

---

#### Phase 3: Pane content capture + state detection

**GitHub Issue: `feat: pane content capture and agent state detection`**

- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **What:**
  - Create `src/cc_monitor/analyzer.py` — `capture_pane(tmux_target: str) -> str` calls `tmux capture-pane -p -t <target>`
  - Implement `detect_claude_state(lines: list[str]) -> str`:
    - `needs_input`: bottom lines contain `❯` prompt + cost bar `$X.XX`, no `⏺` in last 10 lines
    - `working`: contains `⏺` tool markers or thinking indicators, no `❯` at bottom
    - `idle`: completion marker `✻ Worked for` or `✻ Cooked for` visible, prompt at bottom
  - Implement `detect_opencode_state(lines: list[str]) -> str`:
    - `working`: status bar contains timer pattern `\d+m \d+s`
    - `needs_input` / `idle`: status bar has model name, no timer, empty `┃` input area
  - Implement `detect_state(agent_type: str, lines: list[str]) -> str` — dispatches to the correct detector
  - Add unit tests with representative pane content samples from research notes
- **Why:** State detection is the core differentiator — knowing whether an agent is working, idle, or waiting. Research documented exact markers for both agents.
- **Expected impact:** capability_surface +0.3, tests remain green
- **Priority:** high

---

#### Phase 4: Activity summarization

**GitHub Issue: `feat: one-sentence activity summary extraction from pane content`**

- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **What:**
  - Add `summarize_activity(agent_type: str, lines: list[str]) -> str` to `analyzer.py`
  - Claude Code summary extraction:
    - If recap line exists (`※ recap:`), use that text
    - If tool call visible (`⏺ ToolName(args)`), extract "Using ToolName"
    - If thinking, return "Thinking..."
    - Fallback: last non-empty, non-decoration line
  - OpenCode summary extraction:
    - Extract last visible content line that isn't part of the status bar or input area
    - If working with timer, include "Processing for Xm Ys"
    - Fallback: "Active session"
  - Implement `analyze_sessions(sessions: list[AgentSession]) -> list[AgentSession]` — captures pane, detects state, summarizes, returns updated sessions
  - Add unit tests for summary extraction
- **Why:** Activity summary gives the user a quick read on what each agent is doing without switching panes.
- **Expected impact:** capability_surface +0.2, tests remain green
- **Priority:** high

---

#### Phase 5: Rich table display + CLI wiring

**GitHub Issue: `feat: rich table display and CLI entry point`**

- **Category:** EXPLORE
- **Growth dimension:** capability_surface
- **What:**
  - Create `src/cc_monitor/display.py` — `display_results(sessions: list[AgentSession]) -> None`
    - Uses `rich.table.Table` with columns: Tmux Target, Agent, State, Summary
    - Color-codes state: green=idle, yellow=working, red=needs_input
    - Handles empty results: "No agent sessions found in tmux."
  - Create `src/cc_monitor/cli.py` — `main()` function:
    - Calls `discover_sessions()` → `analyze_sessions()` → `display_results()`
    - argparse with `--help` and `--json` flag (outputs JSON instead of table)
    - Exit code 0 always (monitoring tool, not a test)
  - Wire `__main__.py` to call `cli.main()`
  - Update `pyproject.toml` scripts entry: `ccm = "cc_monitor.cli:main"`
  - Add test for display with mock session data (test that it doesn't crash)
  - Add test for `--json` output format
- **Why:** This is the user-facing layer — ties everything together into the `ccm` command. Rich table is the primary output, JSON is for scripting.
- **Expected impact:** capability_surface +0.2, cli_runs eval stays green, tests green
- **Priority:** high

---

#### Phase 6: Structured logging + observability

**GitHub Issue: `feat: add structured logging with loguru`**

- **Category:** EXPLOIT
- **Growth dimension:** observability
- **What:**
  - Add `loguru` dependency to pyproject.toml
  - Create `src/cc_monitor/logging.py` — configure loguru with:
    - Stderr sink at INFO level (default), controlled by `LOGGING_LEVEL` env var
    - File sink to `logs/cc_monitor.log` at DEBUG level
    - Structured JSON format for file sink
  - Add debug logging to discovery.py: log each pane found, classification result, verification result
  - Add debug logging to analyzer.py: log capture timing, state detection result, summary
  - Add info logging to cli.py: log session count found, total scan time
  - Import and initialize logging in `__init__.py`
  - Update tests to ensure logging doesn't break anything
- **Why:** Observability is foundational for the factory to learn from production behavior. loguru is the project's preferred logging library.
- **Expected impact:** observability 0.0 → 0.7, all other evals remain green
- **Priority:** medium

---

#### Phase 7: End-to-end integration test + operational validation

**GitHub Issue: `feat: integration tests and end-to-end validation`**

- **Category:** EXPLOIT
- **Growth dimension:** factory_effectiveness
- **What:**
  - Add integration test in `tests/test_integration.py`:
    - Test full pipeline with mocked subprocess (tmux not required)
    - Mock `list_all_panes` → provide fake pane data with claude + opencode entries
    - Mock `capture_pane` → provide representative terminal content
    - Assert full flow: discover → analyze → display produces expected output
  - Add `tests/test_cli.py`:
    - Test `--help` flag outputs help text
    - Test `--json` flag with mocked sessions produces valid JSON
    - Test with no tmux sessions found (graceful empty result)
  - Ensure all eval dimensions pass: tests, typecheck, lint, cli_runs, formatting
- **Why:** Integration tests validate the full pipeline without needing live tmux. CLI tests ensure the entry point works for the eval harness.
- **Expected impact:** tests eval stays 1.0, factory_effectiveness +0.2
- **Priority:** medium

---

### Anti-patterns to Avoid
- Don't use libtmux — research confirmed subprocess is sufficient for 2 commands
- Don't hardcode Claude Code version strings — use `\d+\.\d+\.\d+` regex pattern
- Don't capture scrollback (`-S -` flag) — only visible content needed for state detection
- Don't add daemon/TUI/persistence — MVP is snapshot only
- Don't add LLM-based summarization — heuristic parsing is sufficient for MVP

## Deferred

- Missing items requiring human intervention: None identified. All features can be built with the information from research.
