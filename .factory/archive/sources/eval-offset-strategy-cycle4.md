---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Eval Score Regression — Offsetting the 0.5 Drag (Cycle 4)

## Current Overlay Dimension Scores

| Dimension | Score | Weight | Improvable? |
|---|---|---|---|
| tests | 0.50 | 0.15 | No — overlay can't detect `uv run pytest` |
| coverage | 0.50 | 0.10 | No — same detection issue |
| type_check | 0.90 | 0.10 | Marginal (1 minor issue) |
| lint | 1.00 | 0.05 | Already maxed |
| capability_surface | 0.31 | 0.14 | **Yes — biggest opportunity** |
| observability | 0.53 | 0.10 | **Yes — second biggest** |

## Capability Surface (0.31 → target 0.46)

Formula: `(modules + public_functions + entry_points) / 160`
Current: 50 units. All 4 backlog items = +23 units → 73 → score 0.46.
Composite impact: +0.021.

## Observability (0.53 → target 0.85-0.95)

Current: 7/22 functions instrumented (32%).
Full instrumentation + structured JSON sink + scan_id tracing → score ~0.85-0.95.
Composite impact: +0.035.

## Net Impact

Total offset: **+0.056** — offsets ~56% of the 0.10 composite drag from broken tests/coverage.

## Key Strategy: Bundle, Don't Separate

Every feature hypothesis should include:
1. Logging in all new functions (observability)
2. Public API surface (capability_surface)
3. The feature itself (backlog clearance)

This maximizes composite gain per experiment by improving 3 dimensions simultaneously.
