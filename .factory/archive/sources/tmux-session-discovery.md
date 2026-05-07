---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# tmux Session Discovery — Detecting Agent Processes

## Key Findings

- `tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_command} #{pane_pid}'` lists all panes across all sessions.
- OpenCode shows `pane_current_command = "opencode"` directly.
- Claude Code shows `pane_current_command` as a **version number** (e.g., `2.1.119`, `2.1.118`) — the binary uses its version string as the process name.

## Detection Strategy (Two-Tier)

1. **Fast path**: Check `pane_current_command` — match `opencode` directly, match version-like patterns (`\d+\.\d+\.\d+`) for Claude Code candidates.
2. **Verify path**: For version-number matches, check child processes of `pane_pid` using `ps -eo pid,ppid,comm` and look for `claude` in the child process names.

## Live System Confirmation (2026-05-07)

```
pane=writer-assistance-cc-opus:1.1  cmd=2.1.119  pid=57697  children=claude
pane=cleanup_gh:2.1                 cmd=2.1.118  pid=22347  children=claude
pane=agents-python-container:2.1    cmd=opencode pid=95294  children=opencode
pane=factory:1.1                    cmd=opencode pid=40301  children=opencode
```

## Pitfalls

- Claude Code version-based detection is fragile — version changes with every update. Must use regex pattern matching plus child process verification, not hardcoded strings.
- Multiple agents per session possible — must scan all panes, not just active ones.

## References

- [tmux wiki — Advanced Use](https://github.com/tmux/tmux/wiki/Advanced-Use)
- [Tao of tmux — Scripting](https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html)
