---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07

## Phase: Post-Research — CEO PROCEED Verdict

### Decision
Proceed to implementation with the researched approach. No pivots or alternative strategies needed.

### Key Strategic Choices

1. **Two-tier detection**: Fast path (pane_current_command regex) + verify path (child process check via `ps`). Handles Claude Code's fragile version-number-as-process-name pattern.

2. **Minimal dependency surface**: subprocess for tmux/process interaction, rich for display. No libtmux, no CLI framework. Single non-stdlib runtime dependency.

3. **Architecture**: Linear pipeline — discover → analyze → display. State in dataclasses, behavior in functions. Matches project philosophy.

4. **Prioritize Claude Code**: Primary detection target. OpenCode support included but Claude Code patterns are the priority for accuracy.

### Constraints from CEO
- Use two-tier detection strategy (fast path + verify path)
- Keep rich as the only non-stdlib dependency beyond dev tools
- Prioritize Claude Code patterns since it's the primary tool

### Risk Assessment
- Claude Code version-based detection is inherently fragile — regex + child process verification mitigates this
- No similar tools exist — novel implementation, but small scope limits risk
- MVP is intentionally constrained: single command, snapshot view, no daemon
