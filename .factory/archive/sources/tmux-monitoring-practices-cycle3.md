---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# tmux Monitoring Best Practices — Cycle 3 Update

## Findings

- **Refresh intervals**: 2-5 seconds is standard (agent-teams-tmux uses 5s, ccm's watch mode uses 2s default — both reasonable).
- **libtmux** (v0.55.1, pre-1.0): Object-oriented tmux API, but adds a heavy dependency and unstable API. ccm's subprocess approach is simpler and sufficient for read-only monitoring.
- **Event-driven updates**: Some tools use fswatch/inotifywait for file-change triggers. Overkill for ccm — periodic poll is simpler and the scan is fast (~50ms).

## Recommendation

Stick with subprocess + periodic poll. libtmux is unstable (pre-1.0) and adds dependency weight for read-only use. Event-driven is overkill given ~50ms scan time.

## Sources

- [libtmux docs](https://libtmux.git-pull.com/quickstart/)
- [agent-teams-tmux](https://lobehub.com/skills/smartassets-io-skills-agent-teams-tmux)
