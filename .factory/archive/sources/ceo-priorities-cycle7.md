---
tags:
  - factory
  - source
  - cc-monitoring-agent
  - strategy
date: 2026-05-07
source: factory-archivist
---

# CEO Priorities — Cycle 7

CEO PROCEED verdict on research. Key directives:

## Feature Priorities (ordered)
1. **Gemini CLI / Codex CLI detection** — strengthens agent-agnostic differentiator, +capability_surface
2. **Pending approval detection refinement** — competitive parity with TmuxCC/ATM, +capability_surface
3. **Observability**: increase function logging coverage to >50% — currently 32% (7/22 functions), +observability
4. **Fix 2 remaining mypy errors** — type_check hygiene

## Context
- Backlog is empty — pure exploration mode
- At least 2 hypotheses MUST target growth dimensions (per budget)
- capability_surface (0.31) is weakest growth dimension — prioritize new features
- Observability (0.53, 32% function coverage) needs improvement
- 15 open GitHub issues are stale from prior experiments — NOT required to address
- No new files — embed all features in existing modules per validated pattern

## Composite Score State
- Factory composite: 0.577 (last eval)
- Project eval: 1.0
- type_check: 0.9 (2 errors remaining)
- tests/coverage: 0.5/0.5 (not detected by factory overlay — known infra issue)
- capability_surface: 0.31 (weakest)
