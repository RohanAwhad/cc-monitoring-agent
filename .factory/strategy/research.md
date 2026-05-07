# Research — cc-monitoring-agent (Improve Cycle)

## Project Summary

cc-monitoring-agent (`ccm`) is a Python CLI tool that discovers Claude Code and OpenCode sessions running in tmux panes, detects their state (working/idle/needs_input), extracts a one-sentence activity summary, and displays results as a rich table or JSON. Architecture: discover → analyze → display pipeline. Tech stack: subprocess + rich + loguru, strict mypy, pytest, ruff.

**Current eval composite: 1.0** (all 5 dimensions pass — tests, typecheck, lint, cli_runs, formatting). The 0.517 score referenced in observations was from a prior cycle; type errors and coverage issues have since been resolved. All 70 tests pass, mypy strict reports 0 errors.

## Backlog Assessment

Backlog contains 1 item: "Missing items requiring human intervention: None identified." — this is a placeholder/empty item, not actionable. The backlog is effectively empty. No items are blocked or obsolete because none are real items.

## Prior Knowledge (Archive)

The archive contains 7 completed build experiments (all kept), 6 source notes covering tmux discovery, pane capture, terminal patterns for both Claude Code and OpenCode, tech stack decisions, and similar project analysis. Key prior decisions:
- **No libtmux** — only 2 tmux commands needed; subprocess suffices
- **No CLI framework** — single command, argparse is enough
- **rich as only non-stdlib dep** (plus loguru for logging)
- **Two-tier detection** — fast pane classification + child process verification
- **Similar projects**: nights-watch (TUI monitor with MCP group chat) — only comparable project found, 0 stars
- **Out-of-scope items noted at build time**: daemon mode, TUI dashboard (rich Live), notification integration, history/persistence, LLM summarization, config file

## External Research Findings

### 1. pytest-cov Configuration for src Layout

The eval currently checks pass/fail but does not measure **test coverage**. Adding coverage measurement would provide a growth signal and guard against regressions.

**Recommended configuration** (from [pytest-cov docs](https://pytest-cov.readthedocs.io/en/latest/config.html), [Scientific Python guide](https://learn.scientific-python.org/development/guides/coverage/), [Coverage.py config reference](https://coverage.readthedocs.io/en/latest/config.html)):

```toml
# pyproject.toml additions
[tool.pytest.ini_options]
addopts = "--cov=cc_monitor --cov-config=pyproject.toml --cov-report=term-missing"

[tool.coverage.run]
source_pkgs = ["cc_monitor"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

Requires adding `pytest-cov` to dev dependencies. The `source_pkgs` key is essential for src-layout projects — using `source = ["src"]` would measure the wrong paths. Coverage.py reads from `pyproject.toml` natively on Python 3.11+.

### 2. mypy src Layout Best Practices

Current config (`strict = true`) works and passes clean. Enhancements from [mypy docs](https://mypy.readthedocs.io/en/stable/config_file.html) and [pydevtools guide](https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/):

```toml
[tool.mypy]
strict = true
packages = ["cc_monitor"]
warn_unreachable = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```

Key findings:
- `packages = ["cc_monitor"]` lets you run `mypy` without path args
- `warn_unreachable` is NOT included in `--strict` but catches dead code paths
- Test overrides are standard practice — test functions often lack return type annotations
- subprocess.run in strict mode: always pass `text=True` as literal (not variable), annotate result types explicitly when wrapping. The heavily overloaded type stubs in typeshed for subprocess.run are the most common source of strict-mode type errors in CLI tools.

### 3. CLI Feature Expansion Patterns

The tool currently has a single command with one flag (`--json`). Standard expansion patterns from [argparse docs](https://docs.python.org/3/library/argparse.html) and [Real Python guide](https://realpython.com/command-line-interfaces-python-argparse/):

**Subcommands via `add_subparsers()`:**
- `ccm status` — current behavior (list all sessions)
- `ccm watch` — continuous polling with live refresh
- `ccm attach <target>` — shortcut to `tmux attach -t`
- `ccm summary` — compact one-line output for shell prompts

Key pattern: `set_defaults(func=handler)` on each subparser, dispatch via `args.func(args)` in main.

**Backward compatibility**: bare `ccm` (no subcommand) should behave as `ccm status`. Achieved by setting `default` on the subparser or checking `hasattr(args, 'func')`.

### 4. Watch Mode Implementation

Watch mode is the highest-impact feature for a monitoring tool — continuous observation is the core use case. Research from [Rich Live display docs](https://rich.readthedocs.io/en/stable/live.html), [system-monitor-cli](https://pypi.org/project/system-monitor-cli/), and [terminal monitoring guide (Medium)](https://medium.com/@cumulus13/building-beautiful-terminal-based-network-monitoring-tools-in-python-6a036514097a):

**Rich `Live` context manager** provides flicker-free terminal refresh:
```python
with Live(table, refresh_per_second=4) as live:
    while True:
        sessions = discover_sessions()
        analyze_sessions(sessions)
        live.update(build_table(sessions))
        time.sleep(interval)
```

Key design points:
- No threading needed — discover+analyze takes ~50ms total, well within a 2s poll interval
- `refresh_per_second` parameter controls render rate independent of data collection rate
- Graceful exit on `KeyboardInterrupt`
- `--interval` flag for configurable poll rate (default 2s)
- Rich `Live` is already available since `rich` is a dependency

### 5. Filtering and Sorting

Low-complexity, high-usability additions:
- `--state working|idle|needs_input` — filter by state
- `--agent claude|opencode` — filter by agent type
- `--sort state|agent|session` — sort output
- Implementation: pure Python filtering/sorting on `list[AgentSession]` before display

### 6. One-Line Summary Mode

For embedding in tmux status bar or shell prompts:
- `ccm summary` or `ccm status --oneline`
- Output: `3 agents: 2 working, 1 idle` or `⚡2 🕐1` (compact)
- Enables integration: `set -g status-right '#(ccm summary --oneline)'` in .tmux.conf

### 7. State Change Notifications

For the "background monitoring" use case:
- `ccm watch --notify` triggers macOS notification when an agent transitions to `needs_input`
- Implementation: track previous state dict between poll iterations, diff on each cycle
- macOS: `osascript -e 'display notification "..." with title "ccm"'` — no extra dependencies
- Requires state persistence across poll cycles (simple dict in watch loop)

## Recommended Focus Areas

### FIX: Add pytest-cov and coverage configuration
- Add `pytest-cov` to dev deps
- Configure `[tool.coverage.run]` and `[tool.coverage.report]` in pyproject.toml
- Set `fail_under = 80` (current coverage is likely high given 70 tests for ~200 LOC)
- Strengthens eval by making test quality measurable, not just pass/fail

### EXPLOIT: Watch mode (`ccm watch`)
- Highest-impact feature — continuous observation is the primary monitoring UX
- Use Rich `Live` context manager for flicker-free refresh
- Add `--interval` flag (default 2s)
- Requires migrating CLI from flat argparse to subcommands (`ccm status`, `ccm watch`)
- Backward compat: bare `ccm` (no subcommand) behaves as `ccm status`
- **Growth dimension:** capability_surface

### EXPLOIT: Filtering and sorting flags
- `--state`, `--agent`, `--sort` flags on the status subcommand
- Low complexity, improves usability when many sessions are running
- Pure Python filtering on `list[AgentSession]`
- **Growth dimension:** capability_surface

### EXPLORE: One-line summary mode
- `ccm summary` or `ccm status --oneline` for tmux status bar / shell prompt integration
- Output: `3 agents: 2 working, 1 idle` compact format
- Enables integration with tmux, starship, or other status tools
- **Growth dimension:** capability_surface

### EXPLORE: State change notifications
- `ccm watch --notify` triggers macOS notification on `needs_input` transitions
- Track previous state between poll iterations (simple dict)
- macOS notification via `osascript` — no extra deps
- **Growth dimension:** capability_surface

## References

- [pytest-cov configuration](https://pytest-cov.readthedocs.io/en/latest/config.html)
- [Coverage.py configuration reference](https://coverage.readthedocs.io/en/latest/config.html)
- [Scientific Python coverage guide](https://learn.scientific-python.org/development/guides/coverage/)
- [pytest good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy strict mode guide (pydevtools)](https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/)
- [mypy common issues](https://mypy.readthedocs.io/en/stable/common_issues.html)
- [argparse documentation](https://docs.python.org/3/library/argparse.html)
- [Real Python argparse guide](https://realpython.com/command-line-interfaces-python-argparse/)
- [Rich Live display](https://rich.readthedocs.io/en/stable/live.html)
- [Building terminal monitoring tools with Rich (Medium)](https://medium.com/@cumulus13/building-beautiful-terminal-based-network-monitoring-tools-in-python-6a036514097a)
- [system-monitor-cli (PyPI)](https://pypi.org/project/system-monitor-cli/)
