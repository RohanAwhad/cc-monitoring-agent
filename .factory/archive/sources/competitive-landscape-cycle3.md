---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Competitive Landscape — Cycle 3 Update

## Key Finding

The competitive landscape has matured significantly since the build phase. Multiple tools now exist for managing Claude Code sessions in tmux.

## New Entrants

- **claude-tmux** (v1.2.0, PyPI): Full-featured manager using SQLite for state tracking via Claude Code plugin hooks (not pane scraping). Features: worktree isolation per agent, TUI dashboard with vim keybindings, attention-based navigation (`next-attention`), search/filter, preview panes, squash-merge workflow. Requires Python 3.12+.
- **tmux-orche** (PyPI): Control plane for inter-agent communication across tmux sessions.
- **pylumbergh** (PyPI): Web dashboard for supervising multiple Claude Code sessions in tmux.
- **claude-code-tools** (PyPI): Programmatic tmux control for Claude Code.

## ccm Differentiation

ccm uses **passive pane scraping** (no plugin hooks required, works with any agent including OpenCode), while claude-tmux uses **active hooks** (requires setup but gets richer state). ccm is lighter-weight and zero-config for monitoring.

## Sources

- [claude-tmux (PyPI)](https://pypi.org/project/claude-tmux/)
- [tmux-orche (PyPI)](https://pypi.org/project/tmux-orche/0.4.16/)
- [pylumbergh (PyPI)](https://pypi.org/project/pylumbergh/0.1.0a143/)
