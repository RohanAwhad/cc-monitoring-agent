---
name: Claude Code Native OTel Support (Cycle 6)
description: Claude Code now exports telemetry via OpenTelemetry — 8 metrics, distributed tracing, TRACEPARENT propagation
type: reference
source: factory-archivist
date: 2026-05-07
tags:
  - factory
  - source
  - cc-monitoring-agent
---

# Claude Code Native OpenTelemetry Support

Claude Code now exports telemetry natively via OpenTelemetry:

- **8 metrics** including `claude_code.token.usage` (by type and model) and `claude_code.session.count`
- **Active time tracking** (excludes idle time)
- **Distributed tracing** with `TRACEPARENT` propagation to subprocesses (beta)
- **Privacy**: prompt text redacted by default, configurable via env vars

## Relevance to ccm

ccm could optionally consume OTel data for richer metrics without requiring hook setup — just reading the metrics endpoint. This would bridge the gap between zero-config pane scraping and hook-based rich metadata without requiring any Claude Code configuration.
