# Research Report — CC Monitoring Agent

## Project Summary

A Python CLI tool that scans all tmux panes, detects running Claude Code and OpenCode sessions, and displays a dashboard showing: what each agent is doing, whether it's waiting for user input, and the tmux coordinates to jump there.

MVP: single command, snapshot view, no daemon or persistence.

---

## Key Research Findings

### 1. Session Discovery — Detecting Agent Processes in tmux

**How `pane_current_command` works:**
- `tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_command} #{pane_pid}'` lists all panes across all sessions.
- OpenCode shows `pane_current_command = "opencode"` directly.
- Claude Code shows `pane_current_command` as a **version number** (e.g., `2.1.119`, `2.1.118`). This is because the Claude Code binary uses its version string as the process name.

**Detection strategy (two-tier):**
1. **Fast path**: Check `pane_current_command` — match `opencode` directly, match version-like patterns (`\d+\.\d+\.\d+`) for Claude Code candidates.
2. **Verify path**: For version-number matches, check child processes of `pane_pid` using `ps -eo pid,ppid,comm` and look for `claude` in the child process names.

**Confirmed from live system (2026-05-07):**
```
pane=writer-assistance-cc-opus:1.1  cmd=2.1.119  pid=57697  children=claude
pane=cleanup_gh:2.1                 cmd=2.1.118  pid=22347  children=claude
pane=agents-python-container:2.1    cmd=opencode pid=95294  children=opencode
pane=factory:1.1                    cmd=opencode pid=40301  children=opencode
```

### 2. Capturing Pane Content

**Best approach**: `tmux capture-pane -p -t '<target>'` piped through subprocess.

```python
result = subprocess.run(
    ["tmux", "capture-pane", "-p", "-t", f"{session}:{window}.{pane}"],
    capture_output=True, text=True
)
content = result.stdout
```

- `-p` outputs to stdout (no buffer save needed).
- No need for `-S -` (full scrollback) — we only need the visible screen for activity detection.
- Fast: ~5-10ms per pane.

**libtmux alternative**: `pane.capture_pane()` returns `list[str]`. Cleaner API but adds a dependency. For MVP, raw subprocess is simpler and sufficient.

### 3. Claude Code Terminal Patterns

Claude Code renders a distinctive TUI with these identifiable patterns:

**Idle / waiting for input:**
```
❯ 
───────────────────────────
  [████████████████░░░░████] $1.430
  ⏵⏵ bypass permissions on (shift+tab to cycle)
```
Key markers: `❯` prompt character, cost indicator `$X.XX`, `⏵⏵` permission mode indicator.

**Active tool use:**
```
⏺ Bash(echo "test")
⎿ (No content)
```
Key markers: `⏺` (tool call indicator), tool name in format `ToolName(args)`.

**Thinking/processing:**
Shows inline progress: "still thinking", "thinking more", "almost done thinking".

**Completion marker:**
```
✻ Worked for 9m 26s
```
or
```
✻ Cooked for 9m 2s
```

**Recap section:**
```
※ recap: Building a writing assistance webapp...
```

### 4. OpenCode Terminal Patterns

OpenCode renders a Bubble Tea TUI with a status bar:

**Idle / waiting for input (bottom bar):**
```
  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                    25.2K (3%) · $0.19  ctrl+p commands
```
Key markers: `▣  Auto-Accept` or model name in status bar, `ctrl+p commands` at bottom right.

**Active processing:**
```
  ▣  Auto-Accept · Claude Opus 4.6 · 3m 53s
```
Key marker: timer duration visible (e.g., `3m 53s`), indicates active processing.

**Waiting for user input:**
The input area shows `┃` (vertical bar) with an empty input line.

### 5. Input Detection Heuristics

**Claude Code — waiting for input:**
- Bottom of pane contains `❯` (the prompt character)
- Bottom section has the cost bar `[████...] $X.XX`
- No active tool call indicator (`⏺`) in the last ~10 lines

**Claude Code — needs permission:**
- Contains permission prompt patterns (yes/no dialog)
- Hook system fires `permission_prompt` event

**Claude Code — actively working:**
- Contains `⏺` tool markers in recent output
- Contains thinking indicators
- No `❯` prompt visible at bottom

**OpenCode — waiting for input:**
- Bottom area has empty `┃` input field
- Status bar shows model name but no active timer with seconds ticking

**OpenCode — actively working:**
- Status bar shows active timer (e.g., `· 3m 53s`)
- Recent content shows tool call output

### 6. Tech Stack Recommendation

| Component | Choice | Rationale |
|---|---|---|
| **tmux interaction** | `subprocess` (raw) | Simpler, no extra dep, 2 commands needed (`list-panes`, `capture-pane`) |
| **Process detection** | `subprocess` + `ps` | Check child processes of pane PIDs |
| **CLI framework** | None (argparse or bare) | Single command, no subcommands needed |
| **Output formatting** | `rich` (Table + Console) | Beautiful tables, color support, widely used |
| **Content parsing** | regex + string matching | Heuristic patterns identified above |
| **Package management** | `uv` + `pyproject.toml` | Standard modern Python tooling |

**Why not libtmux?** For MVP, we call exactly 2 tmux commands. libtmux adds a pre-1.0 dependency (API may change) for no real benefit at this scale. Can adopt later if needed.

**Why rich?** The output is a table of sessions — rich.Table is purpose-built for this. Alternative: plain print with manual alignment, but rich handles terminal width, colors, and Unicode box-drawing for free.

### 7. Architecture Pattern

```
main()
  ├── discover_sessions()        # tmux list-panes → filter for claude/opencode
  │     ├── list_all_panes()     # subprocess: tmux list-panes -a -F ...
  │     └── classify_pane()      # is it claude? opencode? neither?
  ├── analyze_sessions()         # for each session: capture + parse
  │     ├── capture_pane()       # subprocess: tmux capture-pane -p -t ...
  │     ├── detect_state()       # idle? working? needs_input?
  │     └── summarize_activity() # extract one-sentence summary
  └── display_results()          # rich.Table output
```

State model:
```python
@dataclass
class AgentSession:
    session_name: str       # tmux session
    window_index: int       # tmux window
    pane_index: int         # tmux pane
    agent_type: str         # "claude" | "opencode"
    state: str              # "working" | "idle" | "needs_input"
    summary: str            # one-sentence activity description
    pane_pid: int
    tmux_target: str        # "session:window.pane" for jumping
```

### 8. Potential Pitfalls

1. **Claude Code version-based detection is fragile**: The version number in `pane_current_command` will change with every update. Must use pattern matching (`\d+\.\d+\.\d+`) plus child process verification, not hardcoded version strings.

2. **Terminal content has ANSI escapes**: `capture-pane` without `-e` flag strips escape sequences by default — which is what we want. But some Unicode characters (box-drawing, emoji) may still appear and need handling.

3. **Pane content varies by terminal size**: A narrow pane wraps text differently. Summary extraction should work on the last N lines, not fixed positions.

4. **Race condition on state detection**: Between capturing content and displaying results, the state may change. Acceptable for MVP (snapshot tool), but worth noting.

5. **Multiple agents per session**: A tmux session can have multiple windows/panes with different agents. Must scan all panes, not just active ones.

6. **OpenCode TUI uses alternate screen buffer**: Bubble Tea apps often use the alternate screen buffer. `capture-pane` handles this correctly (captures what's visible), but scrollback may not be available.

### 9. MVP Scope

**In scope:**
- Single CLI command: `ccm` or `cc-monitor`
- Scan all tmux panes for Claude Code and OpenCode
- Show table: tmux target, agent type, state, summary
- State detection: working / idle / needs_input
- One-sentence activity summary from visible pane content

**Out of scope (future):**
- Daemon mode / continuous monitoring
- TUI dashboard (textual/rich Live)
- Notification integration
- History / persistence
- LLM-based summarization
- Configuration file

---

## Similar Projects Found

No direct equivalent found. Related tools:
- **tmuxp** — tmux session manager (libtmux-based), manages layout/config, not monitoring
- **tmux-fingers** / **tmux-yank** — tmux plugins for content extraction, not monitoring
- **Claude Code hooks** — built-in notification system for idle/permission states, but per-session, not cross-session dashboard

This tool fills a gap: a single-pane view of all AI coding agents running across tmux sessions.

---

## References

- [libtmux docs — Pane Interaction](https://libtmux.git-pull.com/topics/pane_interaction.html)
- [libtmux on PyPI (v0.55.1)](https://pypi.org/project/libtmux/)
- [tmux wiki — Advanced Use](https://github.com/tmux/tmux/wiki/Advanced-Use)
- [Tao of tmux — Scripting](https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html)
- [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code issue #13024 — WaitingForInput hook](https://github.com/anthropics/claude-code/issues/13024)
- [OpenCode GitHub](https://github.com/opencode-ai/opencode)
- [OpenCode docs](https://opencode.ai/docs/)
- [Rich library](https://github.com/textualize/rich)
- [tmux capture-pane guide](https://tmuxai.dev/tmux-capture-pane/)
- [Under the hood of Claude Code](https://pierce.dev/notes/under-the-hood-of-claude-code)
