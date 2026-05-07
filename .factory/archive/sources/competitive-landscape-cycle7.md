---
tags:
  - factory
  - source
  - cc-monitoring-agent
  - competitive-analysis
date: 2026-05-07
source: factory-archivist
---

# Competitive Landscape — Cycle 7 (Explosive Growth)

The Claude Code monitoring space has exploded since cycle 6. Three distinct categories have emerged:

## Hook-Based Monitoring (structured events, rich metadata)
- **ATM (Agent Tmux Manager)** — Rust TUI + daemon, Claude Code hooks → Unix socket → dashboard. Cost tracking, agent control CLI (spawn/kill/interrupt), workspace layouts.
- **claude-code-hooks-multi-agent-observability** (920 stars) — Hook scripts → HTTP → Bun server → SQLite → WebSocket → Vue dashboard. Live pulse chart, agent swim lanes, MCP tool detection.
- **agents-observe** — Claude plugin install, hook events → API → React dashboard. Subagent relationship tracking.
- **Claude Code Agent Monitor** — Node.js + React + SQLite. Activity heatmap, orchestration DAGs, Sankey diagrams.

## TUI-Based Monitoring (pane scraping, multi-agent)
- **TmuxCC** — Rust TUI. Supports Claude Code, OpenCode, Codex CLI, Gemini CLI. Interactive approval management, subagent tracking, 500ms polling.
- **Agent Deck** — Multi-agent TUI with Telegram + Slack bridges for remote monitoring.
- **Workmux** — Git worktrees + tmux windows, agent status overview.

## OTel-Based Monitoring (enterprise, metrics/cost)
- **claude-code-otel** — Full Grafana stack (OTel Collector → Prometheus + Loki → Grafana). DAU/WAU/MAU.
- **Datadog AI Agents Console** — Enterprise adoption tracking, cost/ROI analysis.
- **Dynatrace Claude Code Monitoring** — End-to-end OTel visibility.
- **Sentry AI Monitoring** — Token usage, API costs, tool activity per session.

## Key Shift
Claude Code now has **native OpenTelemetry support** (8 metrics, distributed tracing beta, `TRACEPARENT` propagation). Hook-based and OTel approaches are now first-class; pane scraping is the lightweight alternative.

## ccm Position
- **Strengths**: Zero-config, agent-agnostic (OpenCode + Claude Code), fast (~50ms), composable (--json, summary)
- **Gaps**: No interactive approval, no cost/token tracking, no subagent visibility, no persistent history, no remote monitoring
