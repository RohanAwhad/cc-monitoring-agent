---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (H1 Complete — mypy Fix)

## Experiment Outcome
H1 (fix mypy strict-mode type errors) completed and kept. First improve-cycle experiment. Score jumped from 0.517 to 1.0.

## What Was Fixed
All 12 mypy errors traced to a single root cause in `analyzer.py`: functions returning `str` instead of the `AgentState` literal type, and accepting `str` instead of `Literal["claude", "opencode"]` for agent_type. A `cast()` call masked the issue during the build phase.

## Impact on Strategy
- **type_check**: 0.4 → 1.0 (dimension fully resolved)
- **Composite**: 0.517 → 1.0 (all dimensions green per Builder eval)
- H1 is complete. Remaining hypotheses: H2 (pytest-cov), H3 (watch mode), H4 (observability)

## Remaining Improve-Cycle Work
| Hypothesis | Category | Target Dimension | Status |
|---|---|---|---|
| H1: Fix mypy errors | FIX | type_check | **DONE** |
| H2: Configure pytest-cov | FIX | tests, coverage | Pending |
| H3: Watch mode (Rich Live) | EXPLOIT | capability_surface | Pending |
| H4: Expand observability | EXPLOIT | observability | Pending |

## Key Lesson
Build-phase workarounds (like `cast()`) can mask type errors that surface under strict mode. Tightening types at the source is always cheaper than patching downstream.
