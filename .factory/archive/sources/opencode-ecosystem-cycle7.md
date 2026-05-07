---
tags:
  - factory
  - source
  - cc-monitoring-agent
  - ecosystem
date: 2026-05-07
source: factory-archivist
---

# OpenCode Ecosystem Update — Cycle 7

OpenCode has reached 150k+ GitHub stars with significant architecture evolution:

## Key Developments
- **opencode-plugin-otel** — OTel exporter mirroring Claude Code's telemetry signals
- **Client/server architecture** — headless server + multiple frontends
- **Agent system** — plan/build modes for structured development
- **LSP integration** — code intelligence built in
- **Non-interactive scripting mode** — automation-friendly

## Relevance to ccm
OpenCode and Claude Code are converging on similar architectures (OTel, agent modes, subagent orchestration). ccm remains one of the few tools that monitors both, reinforcing the agent-agnostic differentiator. The opencode-plugin-otel means ccm could potentially consume OTel data from both agents via a unified interface.
