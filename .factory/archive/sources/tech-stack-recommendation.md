---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Tech Stack Recommendation

## Chosen Stack

| Component | Choice | Rationale |
|---|---|---|
| tmux interaction | `subprocess` (raw) | Simpler, no extra dep, only 2 commands needed |
| Process detection | `subprocess` + `ps` | Check child processes of pane PIDs |
| CLI framework | None (argparse or bare) | Single command, no subcommands needed |
| Output formatting | `rich` (Table + Console) | Beautiful tables, color support, widely used |
| Content parsing | regex + string matching | Heuristic patterns from live observation |
| Package management | `uv` + `pyproject.toml` | Standard modern Python tooling |

## Key Decisions

- **No libtmux**: Only 2 tmux commands needed. libtmux is pre-1.0 (API may change) — adds dependency for no real benefit at MVP scale.
- **rich as only non-stdlib dep**: Output is a table of sessions — rich.Table is purpose-built. Handles terminal width, colors, Unicode box-drawing.
- **No CLI framework**: Single command tool, no subcommands. argparse or bare is sufficient.

## Architecture Pattern

```
main()
  +-- discover_sessions()        # tmux list-panes -> filter for claude/opencode
  |     +-- list_all_panes()     # subprocess: tmux list-panes -a -F ...
  |     +-- classify_pane()      # is it claude? opencode? neither?
  +-- analyze_sessions()         # for each session: capture + parse
  |     +-- capture_pane()       # subprocess: tmux capture-pane -p -t ...
  |     +-- detect_state()       # idle? working? needs_input?
  |     +-- summarize_activity() # extract one-sentence summary
  +-- display_results()          # rich.Table output
```

## Data Model

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
