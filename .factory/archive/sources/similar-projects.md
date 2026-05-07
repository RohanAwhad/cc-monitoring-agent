---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Similar Projects Survey

## Finding

No direct equivalent found. This tool fills a gap: a single-pane view of all AI coding agents running across tmux sessions.

## Related Tools

- **tmuxp** — tmux session manager (libtmux-based). Manages layout/config, not monitoring.
- **tmux-fingers** / **tmux-yank** — tmux plugins for content extraction, not monitoring.
- **Claude Code hooks** — built-in notification system for idle/permission states, but per-session only. Not a cross-session dashboard.

## Implications

Novel tool — no existing implementation to fork or adapt. Must build from scratch, but scope is small (MVP is a single-command snapshot tool).
