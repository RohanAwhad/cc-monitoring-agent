# Research Report — cc-monitoring-agent (Cycle 3)

## Project Summary

cc-monitoring-agent (`ccm`) is a Python CLI tool that scans tmux panes, detects Claude Code and OpenCode sessions, and displays a status dashboard. Architecture: discover → analyze → display pipeline. Stack: argparse + subprocess + rich + loguru. Current state on main: flat CLI (no subcommands), snapshot-only view, `--json` flag. 81 tests, 98% coverage, project eval 1.0, factory composite 0.539.

**Key constraint**: 4 open PRs from cycle 1 (#2 mypy fix, #5 pytest-cov, #7 watch mode, #9 observability) exist on experiment branches but are not merged to main. All 3 cycle 2 backlog items (filtering, summary, notifications) were correctly implemented but reverted due to systemic factory eval failure (system Python can't resolve src-layout imports for mypy overlay).

## Backlog Assessment

| Item | Status | Achievable? | Notes |
|---|---|---|---|
| Filtering/sorting flags (`--state`, `--agent`, `--sort`) | Tried, reverted (eval blocker) | Yes, if eval blocker resolved | Code was correct, e2e passed, project eval 1.0 |
| One-line summary mode (`ccm summary`) | Tried, reverted (eval blocker) | Yes, if eval blocker resolved | Same — functionally complete, eval-blocked |
| State change notifications (`--notify`) | Tried, reverted (eval blocker) | Yes, if eval blocker resolved | Same — requires watch mode PR #7 merged first |

All 3 items are **blocked by the same root cause**: factory eval runs mypy with system Python, which cannot resolve `src/cc_monitor/` imports. Any new Python code triggers false score regression.

## Prior Knowledge (Archive)

### Relevant Patterns
1. **Factory eval systemic regression**: src-layout projects scored with system Python — root cause of all cycle 2 reverts. `mypy_path = "src"` in pyproject.toml is the project-level fix (new finding this cycle).
2. **0% keep rate = infrastructure blocker**: Stop cycling and fix infrastructure first.
3. **Subcommand refactoring preserves backward compat with default_subparser**: Already applied in PR #7.
4. **Observability instrumentation needs no new tests at debug level**: Applied in cycle 1 H4.
5. **Request-level tracing via context-bound IDs**: Applied in cycle 1 H4 (scan_id).

### Prior Source Notes (Still Valid)
- Watch mode implementation pattern (Rich `Live`, ~50ms scan, no threading)
- One-line summary format (`3 agents: 2 working, 1 idle`)
- CLI subcommand structure (argparse `add_subparsers`)
- macOS osascript notification pattern (now updated with Sequoia caveat — see below)

## External Research Findings

### 1. Competitive Landscape — Significant New Entrants

Since the build phase, the competitive landscape has matured considerably:

- **[claude-tmux](https://pypi.org/project/claude-tmux/)** (v1.2.0): Full-featured manager for multiple Claude Code instances in tmux. Uses SQLite for state tracking via Claude Code plugin hooks (not pane scraping). Features: worktree isolation per agent, TUI dashboard with vim keybindings, attention-based navigation (`next-attention`), search/filter, preview panes, squash-merge workflow. Requires Python 3.12+.
- **[tmux-orche](https://pypi.org/project/tmux-orche/)**: Control plane for inter-agent communication across tmux sessions.
- **[pylumbergh](https://pypi.org/project/pylumbergh/)**: Web dashboard for supervising multiple Claude Code sessions in tmux.
- **[claude-code-tools](https://pypi.org/project/claude-code-tools/)**: Programmatic tmux control for Claude Code.

**Key differentiation for ccm**: ccm uses passive pane scraping (no plugin hooks required, works with any agent including OpenCode), while claude-tmux uses active hooks (requires setup but gets richer state). ccm is lighter-weight and zero-config for monitoring.

### 2. Rich Live vs Textual for TUI Features

- **Rich `Live` + `Table`**: Sufficient for watch mode (flicker-free refresh, no threading needed). Already archived in prior research. Does NOT support interactive filtering/sorting natively.
- **[Textual `DataTable`](https://textual.textualize.io/widgets/data_table/)**: Full interactive table with cursor modes (cell/row/column/none), programmatic `sort(*columns, key=...)`, vim-style navigation. No built-in filtering API — must be implemented via remove/re-add rows. Adds `textual` dependency.
- **Recommendation for ccm**: Stay with Rich `Live` + pre-filter approach. Filtering via CLI flags (`--state`, `--agent`) is simpler and more composable (pipes, scripts) than interactive TUI filtering. Sorting via `--sort` flag with Python `sorted()` on `list[AgentSession]` is trivial. No new dependency needed.

### 3. macOS Notifications — osascript Reliability Issue on Sequoia

**Critical finding**: `osascript -e 'display notification ...'` silently fails on macOS Sequoia and later when the terminal app lacks notification permissions. The command exits 0 (no error) but the notification is dropped. This is a chicken-and-egg problem: terminal apps don't appear in System Settings → Notifications until they've successfully delivered a notification.

**Workarounds** (ranked by reliability):
1. **`terminal-notifier`** (`brew install terminal-notifier`): Registers as its own Notification Center app, sidesteps the permission issue entirely. Most reliable for automation.
2. **One-time Script Editor permission grant**: Run `display notification` in Script Editor first to trigger permission prompt.
3. **Fallback to `display dialog`**: Works without permissions but creates a modal dialog, not a banner.

**Recommendation for ccm**: Use `terminal-notifier` as primary (check availability via `shutil.which`), fall back to `osascript` with a warning about permissions. Document the Sequoia issue in help text.

Sources: [macOS Notification Issue](https://forum.latenightsw.com/t/trying-to-use-terminal-for-display-notification/5068), [Silent Fail Bug](https://github.com/gsd-build/gsd-2/issues/2632), [macOS Notification Best Practices](https://dev.to/jfpio/how-to-get-macos-notifications-for-long-running-processes-even-over-ssh-154d)

### 4. CLI Subcommand Patterns

Current state on main: flat argparse (no subcommands). PR #7 (watch mode) introduces subcommands but isn't merged.

**Best practices** (2025-2026):
- argparse `add_subparsers()` with `set_defaults(func=handler)` is the zero-dependency pattern. Already used in PR #7.
- Click (38.7% of CLI projects) and Typer offer cleaner decorator syntax but add dependencies.
- **Recommendation**: Stay with argparse. ccm has 4 subcommands max — the complexity threshold for Click/Typer isn't reached.

Sources: [CLI Tools Comparison](https://dasroot.net/posts/2025/12/building-cli-tools-python-click-typer-argparse/), [argparse Subparsers](https://runebook.dev/en/docs/python/library/argparse/argparse.ArgumentParser.add_subparsers)

### 5. Factory Eval Blocker — mypy src-layout Fix

The systemic eval blocker (system Python can't resolve src-layout imports) has a project-level workaround:

```toml
[tool.mypy]
mypy_path = "src"
```

This tells mypy where to find packages even when not running from a virtualenv. If the factory eval runs `python -m mypy src/` with system Python, setting `mypy_path = "src"` in pyproject.toml should resolve the import failures.

**Alternative**: `mypy_path = "$MYPY_CONFIG_FILE_DIR/src"` for config-relative resolution.

**This is the highest-priority fix**: unblocking the eval infrastructure makes all 3 backlog items viable again.

Sources: [mypy config docs](https://mypy.readthedocs.io/en/stable/config_file.html), [mypy running imports](https://mypy.readthedocs.io/en/stable/running_mypy.html), [src-layout packaging](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

### 6. tmux Monitoring Best Practices

From the broader ecosystem:
- **Refresh intervals**: 2-5 seconds is standard (agent-teams-tmux uses 5s, ccm's watch mode uses 2s default — both reasonable)
- **libtmux** (v0.55.1, pre-1.0): Object-oriented tmux API, but adds a heavy dependency and unstable API. ccm's subprocess approach is simpler and sufficient for read-only monitoring.
- **Event-driven updates**: Some tools use fswatch/inotifywait for file-change triggers. Overkill for ccm — periodic poll is simpler and the scan is fast (~50ms).

Sources: [libtmux docs](https://libtmux.git-pull.com/quickstart/), [agent-teams-tmux](https://lobehub.com/skills/smartassets-io-skills-agent-teams-tmux)

## Recommended Focus Areas

### Priority 0: Unblock the Eval (FIX)
Add `mypy_path = "src"` to `[tool.mypy]` in pyproject.toml. This is a 1-line config change that may unblock all new Python code from triggering false mypy regressions in the factory eval. Should be tested by running `python -m mypy src/` (not `uv run`) to verify system Python can resolve imports.

### Priority 1: Merge Open PRs (FIX)
PRs #2, #5, #7, #9 represent cycle 1 work that passed all checks. Merging them to main is prerequisite for cycle 2 backlog items (filtering, summary, notifications all depend on the subcommand architecture from PR #7).

### Priority 2: Re-apply Backlog Items (EXPLOIT)
Once eval is unblocked and PRs merged, the 3 reverted features can be re-applied. The implementations were correct — they just need the infrastructure fix:
- Filtering/sorting flags (`--state`, `--agent`, `--sort`)
- One-line summary mode (`ccm summary`)
- State change notifications (`--notify`) — with updated `terminal-notifier` fallback for macOS Sequoia

### Priority 3: New Ideas (EXPLORE)
If cycle 3 has budget for new items beyond backlog:
- **`ccm attach <target>`**: Shortcut to `tmux attach -t` for the selected session — simple quality-of-life improvement, minimal code.
- **tmux status bar integration docs**: `set -g status-right '#(ccm summary --oneline)'` — document this pattern and ensure `ccm summary` output is compatible (no ANSI escape codes, newline handling).

## References

- [claude-tmux (PyPI)](https://pypi.org/project/claude-tmux/)
- [tmux-orche (PyPI)](https://pypi.org/project/tmux-orche/0.4.16/)
- [pylumbergh (PyPI)](https://pypi.org/project/pylumbergh/0.1.0a143/)
- [Textual DataTable](https://textual.textualize.io/widgets/data_table/)
- [Rich Live Display docs](https://rich.readthedocs.io/en/latest/live.html)
- [Rich Table API](https://rich.readthedocs.io/en/stable/reference/table.html)
- [mypy config file docs](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy running imports](https://mypy.readthedocs.io/en/stable/running_mypy.html)
- [Python src-layout vs flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [CLI Tools: Click, Typer, argparse (2025)](https://dasroot.net/posts/2025/12/building-cli-tools-python-click-typer-argparse/)
- [argparse subparsers docs](https://runebook.dev/en/docs/python/library/argparse/argparse.ArgumentParser.add_subparsers)
- [macOS Notification permissions issue](https://forum.latenightsw.com/t/trying-to-use-terminal-for-display-notification/5068)
- [macOS osascript silent fail bug](https://github.com/gsd-build/gsd-2/issues/2632)
- [macOS Notification best practices](https://dev.to/jfpio/how-to-get-macos-notifications-for-long-running-processes-even-over-ssh-154d)
- [libtmux docs](https://libtmux.git-pull.com/quickstart/)
- [agent-teams-tmux](https://lobehub.com/skills/smartassets-io-skills-agent-teams-tmux)
- [Claude Code Agent Teams docs](https://code.claude.com/docs/en/agent-teams)
