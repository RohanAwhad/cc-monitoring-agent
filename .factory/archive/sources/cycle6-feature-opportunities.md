---
name: Cycle 6 Feature Opportunities — Ranked by Value-to-Effort
description: Seven feature candidates for ccm cycle 6, ranked by value/effort, informed by competitive gap analysis
type: reference
source: factory-archivist
date: 2026-05-07
tags:
  - factory
  - source
  - cc-monitoring-agent
---

# Feature Opportunities — Cycle 6

Ranked by value-to-effort ratio, informed by competitive analysis.

## Tier 1: Quick Wins (embed in existing modules, no new files)

### A. `ccm attach <target>` — Quick Jump (LOW effort, HIGH value)
Switch to a specific agent's tmux pane. `tmux select-window`/`select-pane`. Every competitor (TmuxCC, ATM, Workmux) offers this. ~15 lines in `cli.py`.

### B. Pending Approval Detection (LOW effort, MEDIUM value)
Detect pending approval prompts and surface a count in status table. Enhance `analyzer.py` state detection. ~20 lines.

### C. tmux Status Bar Docs/Optimization (LOW effort, LOW-MEDIUM value)
Ensure `ccm summary` output is clean for `set -g status-right '#(ccm summary)'` embedding. `--no-color` flag if missing.

## Tier 2: Differentiating Features (moderate effort, high value)

### D. Token/Cost Estimation from Conversation Files (MEDIUM effort, HIGH value)
Read Claude Code's local JSONL conversation logs (`~/.claude/projects/*/conversations/*.jsonl`), extract token usage. Add `--costs` flag. Unique among pane-scraping tools — hook-level data without hooks.

### E. Gemini CLI + Codex CLI Support (MEDIUM effort, MEDIUM value)
TmuxCC already supports 4 agent types. Extend `discovery.py` and `analyzer.py`. Strengthens "works with any agent" positioning.

## Tier 3: Larger Features (future cycles)

### F. Session History Log (MEDIUM effort, MEDIUM value)
Append state transitions to JSONL during watch mode. `ccm history` subcommand.

### G. Remote Notifications — Slack/Telegram (HIGH effort, MEDIUM value)
Agent Deck offers Telegram and Slack bridges. Higher complexity due to auth/tokens.
