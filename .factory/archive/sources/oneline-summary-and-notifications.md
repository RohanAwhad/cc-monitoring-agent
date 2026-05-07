---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# One-Line Summary Mode and State Change Notifications

## One-Line Summary

For embedding in tmux status bar or shell prompts:
- `ccm summary` or `ccm status --oneline`
- Output: `3 agents: 2 working, 1 idle` or compact icon format
- Enables integration: `set -g status-right '#(ccm summary --oneline)'` in .tmux.conf
- Works with tmux, starship, or other status tools

## State Change Notifications

For background monitoring use case:
- `ccm watch --notify` triggers macOS notification when agent transitions to `needs_input`
- Implementation: track previous state dict between poll iterations, diff on each cycle
- macOS: `osascript -e 'display notification "..." with title "ccm"'` — no extra dependencies
- Requires state persistence across poll cycles (simple dict in watch loop)
