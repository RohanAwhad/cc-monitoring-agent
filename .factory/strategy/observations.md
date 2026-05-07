# Interaction Study — cc-monitoring-agent

Analyzed 21 conversation log(s), 25 relevant messages.

## User Messages (2)
- Project: /Users/rawhad/factory-projects/cc-monitoring-agent
Mode: build

## Project Specification

cc monitoring agent

Run Build mode: the project is new or incomplete. Follow the Build mode pipeline
- yes, so i want a monitoring agent, that will look for all the claude code / opencode sessions on this machine, and it will show me which agent is doing what in like a sentence. Then it also needs to d

## Errors and Issues (23)
- 6. **Structured logging** — loguru with file sink, debug logging across discovery/analyzer, LOGGING_LEVEL env var
- Good, I have full context. Now let me check for the GitHub issue and read any fixed surfaces to avoid.
- Line too long. Let me fix that.
- Now add the test fixtures and test classes at the end of the file.
- The `state` field on `AgentSession` is a `Literal` type but `detect_state` returns `str`. Let me fix `analyze_sessions` to cast properly.
- Import sorting issue. Let me fix it.
- Good — project state is `has_factory`, no research target, so this is **Improve mode**. Current composite score is **0.517**. Weakest dimensions: type_check (0.4, 12 errors), capability_surface (0.31)
- Two issues: module not found (need to configure `src` layout in pyproject.toml) and the deprecated `tool.uv.dev-dependencies`. Let me fix both.
- 4/5 passing. The test fails because `main()` calls `argparse.parse_args()` which reads `sys.argv` and picks up pytest's arguments. I need to fix the test to isolate `sys.argv`.
- Now adding debug logging to discovery.py.
- Now adding debug logging to analyzer.py.
- Line length issues and formatting. Let me fix those.
- Good, formatting is fixed. Let me re-run all checks.
- - **`src/cc_monitor/logging.py`** — loguru config with stderr sink (INFO default, controlled by `LOGGING_LEVEL` env var) and file sink (`logs/cc_monitor.log` at DEBUG, structured format, 10MB rotation
- - **`discovery.py`** — debug logs for pane count, classification results, and claude candidate verification
- - **`analyzer.py`** — debug logs for per-session state detection, summary, and capture timing (ms)
- Pre-existing lint issues in `test_discovery.py` and some in my new file. Let me fix the issues in my file and also the pre-existing ones since ruff needs a clean run.
- Now fix the pre-existing issues in `test_discovery.py`.
- Import sorting issues remain. Ruff is complaining about isort-style grouping. Let me fix with `ruff format`.
- Fixing the lint issues — unused imports in my test file and the line length issue.
- All 17 tests pass and mypy is clean. Let me run the full test suite and ruff to make sure nothing is broken.
- Import sort issue. Let me fix it.
- The existing test also has lint issues — ruff wants isort-style grouping. Let me just fix mine to be clean.

## Similar Projects
- [jakebuild/nights-watch](https://github.com/jakebuild/nights-watch) (0 stars) — TUI for monitoring Claude Code / opencode agents in tmux, with MCP group chat

## Open GitHub Issues
No open issues found (or not a GitHub repo).

## Backlog

**1 items** in the backlog. Clear as many as possible this cycle.

- Missing items requiring human intervention: None identified. All features can be built with the information from research.

## Observability Coverage
- **Score:** 50.0%
- **Function coverage:** 6/18 functions have logging (33%)
- **Total log statements:** 14
- **Structured logging:** Yes
- **Request tracing:** No

### Observability Recommendations
- Add request ID tracing (contextvars + unique ID per request) for end-to-end request correlation
- Improve logging coverage: only 6/18 functions (33%) have log statements

## Prior Knowledge (Obsidian)
No prior notes found.

## Hypothesis Budget

**Backlog items: 1** (clear as many as possible this cycle)
**New items: at most 2** (researcher/strategist may add new ideas)
**Growth minimum: 2** (at least 2 hypotheses must target growth dimensions)

### Rules

- Read the backlog first. Pick items to implement this cycle — no cap on clearing.
- You may add at most 2 NEW items that aren't already in the backlog.
- At least 2 hypotheses must target growth dimensions (capability_surface, factory_effectiveness, research_grounding, experiment_diversity, observability). Each MUST have a `**Growth dimension:**` tag.
- FEEC ordering applies for prioritizing within the backlog (FIX > EXPLOIT > EXPLORE > COMBINE).
- Your open GitHub issues and critical bugs should be addressed as FIX hypotheses.
- Community issues (filed by others) must NOT be auto-fixed — suggest the author creates a PR instead.
- Write any new items not implemented this cycle to a `## New Backlog Items` section in current.md.

*Budget is configurable: set `min_growth`, `max_new` in factory.md under `## Hypothesis Budget`, or pass `--min-growth`, `--max-new` on the CLI.*