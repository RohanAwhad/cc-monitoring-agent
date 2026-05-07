# Researcher Agent Output

- **timestamp:** 2026-05-07T17:41:51Z
- **exit_code:** 0

---

Research report written to `.factory/strategy/research.md`. Key findings:

- **Eval blocker fix found**: Adding `mypy_path = "src"` to `[tool.mypy]` in pyproject.toml should let system Python's mypy resolve src-layout imports — this 1-line config change could unblock all 3 reverted backlog items.
- **Competitive landscape changed**: `claude-tmux` (v1.2.0) is now a full-featured competitor using plugin hooks + SQLite. ccm's differentiation is zero-config passive pane scraping that works with any agent.
- **macOS Sequoia notification issue**: `osascript display notification` silently fails without terminal permissions. Recommendation: use `terminal-notifier` as primary, `osascript` as fallback.
- **Textual not needed**: Rich `Live` + CLI-flag filtering is simpler and more composable than interactive TUI filtering. No new dependency.
- **All 3 backlog items remain achievable** — the implementations were correct, just eval-blocked.
