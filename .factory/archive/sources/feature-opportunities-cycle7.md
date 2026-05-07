---
tags:
  - factory
  - source
  - cc-monitoring-agent
  - feature-analysis
date: 2026-05-07
source: factory-archivist
---

# Feature Opportunities — Cycle 7

Ranked by value-to-effort ratio, informed by competitive gaps:

## Tier 1: Quick Wins (no new files)
1. **`ccm attach <target>`** — Quick jump to agent's tmux pane. ~15 lines in cli.py. Every competitor has this. *(Already delivered in cycle 6)*
2. **Pending approval detection** — Detect pending prompts, surface count in status table. ~20 lines in analyzer.py. Competitive parity with TmuxCC/ATM.
3. **tmux status bar optimization** — Ensure `ccm summary` output is clean for `set -g status-right`.

## Tier 2: Differentiating Features (moderate effort)
4. **Token/cost estimation** — Read Claude Code's local JSONL conversation logs for token counts. `--costs` flag. Unique among pane-scraping tools. *(Already delivered in cycle 6)*
5. **Gemini CLI + Codex CLI detection** — Extend discovery.py/analyzer.py. TmuxCC already supports 4 agents. Strengthens agent-agnostic differentiator.

## Tier 3: Larger Features (future cycles)
6. **Session history log** — Append state transitions to JSONL during watch. `ccm history` subcommand.
7. **Remote notification bridges** — Slack webhook or Telegram bot for `--notify`.

## CEO Feature Priorities (Cycle 7)
1. Gemini CLI / Codex CLI detection (+capability_surface)
2. Pending approval detection refinement (+capability_surface)
3. Observability: increase function logging coverage >50% (+observability)
4. Fix 2 remaining mypy errors (+type_check hygiene)
