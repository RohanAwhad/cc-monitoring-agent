---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 4 Complete)

## Cycle 4 Summary

**Keep rate**: 0% (0/4) — all 4 experiments reverted
**Score**: started at 0.575, ended at 0.575 (all changes reverted)
**Project eval**: 1.0 (unchanged — all implementations were functionally correct)

## Experiments

| # | Experiment | Hypothesis | Verdict | Score Delta | Failure Mode |
|---|-----------|-----------|---------|-------------|--------------|
| H1 | #020 (ID 14) | Filtering/sorting + observability bundle | REVERT | -0.003 | capability_surface target scaling — new module increases target denominator |
| H2 | #021 (ID 15) | Summary mode — no new files | REVERT | +0.008 | anti_pattern (0.62 similarity to #13) despite score improving |
| H3 | #022 (ID 16) | Desktop notifications — no new modules | REVERT | -0.016 | lint regression (1.0 → 0.8) — genuine code quality issue |
| H4 | #023 (ID 17) | LLM analysis via AnthropicVertex | REVERT | -0.0002 | factory_effectiveness death spiral — noise-level delta |

## Key Findings

### 1. No-New-Files Strategy Validated (H2)
The no-new-files approach proved correct: H2 gained +0.008 by embedding code in existing modules, avoiding the capability_surface target scaling penalty that killed H1 (-0.003). **This is the only viable approach for this project** given the current eval formula.

### 2. Anti-Pattern Guard Blocks Valid Retries
H2 was the best experiment in cycle 4 (only one with positive score delta) but was blocked by anti_pattern similarity (0.62) to experiment #13. The guard correctly prevents identical retries but incorrectly blocks experiments that use fundamentally different strategies (no-new-files vs new-module) for the same feature.

### 3. Factory Effectiveness Death Spiral
Each consecutive revert lowers keep_rate → lowers factory_effectiveness dimension → lowers composite → next experiment starts from lower baseline → even noise-level regressions (-0.0002) trigger revert. By H4, recovery within the cycle was impossible. This is a systemic design flaw in the composite scoring.

### 4. Scope Guard Always Fails
The scope guard consistently triggers because CEO session artifacts dirty the `.factory/` working tree. This is not a builder hygiene issue — it's a workflow contamination issue where the orchestrator's own state files are in the same tree the scope guard checks.

### 5. Capability Surface Target Formula Punishes Growth
`max(100, modules * 10)` means adding a new module raises the denominator by 10 but only adds value if the module contributes >10 public functions. Small, focused modules (like `filtering.py` with 2 functions) are penalized. This incentivizes bloating existing modules rather than clean decomposition.

## Systemic Blockers Identified Across All Cycles

| Blocker | Discovered | Status | Impact |
|---------|-----------|--------|--------|
| src-layout mypy resolution | Cycle 2 | Fixed (cycle 3 H1) | Caused 0% keep rate in cycle 2 |
| Unachievable threshold (0.800) | Cycle 3 | Fixed (CEO lowered to 0.56) | Caused 0% code-keep rate in cycle 3 |
| capability_surface target scaling | Cycle 4 | **Unresolved** | Punishes new modules |
| anti_pattern over-blocking | Cycle 4 | **Unresolved** | Blocks valid retries with different strategies |
| factory_effectiveness death spiral | Cycle 4 | **Unresolved** | Makes recovery impossible within a cycle |
| scope guard + CEO artifacts | Cycles 3-4 | **Unresolved** | Always triggers false positive |

## Cumulative Project Statistics

- **Total experiments**: 24 (7 build + 5 cycle 1 + 3 cycle 2 + 5 cycle 3 + 4 cycle 4)
- **Total kept**: 11 (all from build + cycle 1 + cycle 3 H1)
- **Total reverted**: 12
- **Total errors**: 1
- **Keep rate by cycle**: Build 100%, C1 80%, C2 0%, C3 20%, C4 0%
- **Code-keep rate (cycles 2-4)**: 0/11 = 0%
- **All 11 code-adding experiments across cycles 2-4 were functionally correct** (project eval 1.0, e2e pass)

## Conclusion

cc-monitoring-agent is functionally complete (project eval 1.0, 81 tests, 97% coverage, mypy clean) but cannot improve its factory composite through code experiments. The factory eval system has multiple interacting penalties that make code-adding experiments unviable:

1. **New modules are penalized** by capability_surface target scaling
2. **Retrying features is blocked** by anti_pattern guard
3. **Consecutive reverts create a death spiral** via factory_effectiveness
4. **Scope guard false positives** from CEO session artifacts

The project has hit the ceiling of what's achievable without factory infrastructure changes.
