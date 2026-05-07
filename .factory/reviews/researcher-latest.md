# Researcher Agent Output

- **timestamp:** 2026-05-07T15:01:43Z
- **exit_code:** 0

---

Done. Here's what was produced:

**Research report** at `.factory/strategy/research.md` covering:
- **Session discovery**: Claude Code shows as version numbers (`2.1.119`) in `pane_current_command`, OpenCode shows as `opencode`. Verified on live system with child process detection fallback.
- **Terminal patterns**: Documented exact visual markers for idle, working, and needs-input states for both Claude Code (`❯`, `⏺`, `✻`) and OpenCode (`▣ Auto-Accept`, timer, `┃` input area).
- **Tech stack**: raw subprocess for tmux (2 commands needed), `rich.Table` for output, regex for content parsing, no libtmux dependency for MVP.
- **Architecture**: `discover_sessions()` -> `analyze_sessions()` -> `display_results()` with an `AgentSession` dataclass.
- **Pitfalls**: Version-based detection fragility, alternate screen buffer for OpenCode, race conditions.

**Eval profile** at `.factory/eval_profile.json` — 5 dimensions: tests (0.40), typecheck (0.25), lint (0.15), cli_runs (0.15), formatting (0.05).

**Eval script** at `eval/score.py` — runs all dimensions and outputs JSON score report.
