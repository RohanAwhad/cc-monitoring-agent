---
tags:
  - factory
  - source
  - cc-monitoring-agent
  - telemetry
date: 2026-05-07
source: factory-archivist
---

# Claude Code Native OTel Capabilities — Cycle 7

Claude Code now exports telemetry via OpenTelemetry natively:

## Metrics (8 total)
- `claude_code.token.usage` — by type (input/output/cache) and model
- `claude_code.session.count` — active session tracking
- Active time tracking (excludes idle time)

## Tracing
- Distributed tracing with `TRACEPARENT` propagation to subprocesses (beta)
- Enables correlation across parent/child agent sessions

## Privacy
- Prompt text redacted by default
- Configurable via env vars for opt-in

## Relevance to ccm
ccm could optionally consume OTel metrics for richer data without hook setup — just reading the metrics endpoint. This would complement passive pane scraping with structured telemetry, keeping the zero-config philosophy (OTel data is emitted automatically).
