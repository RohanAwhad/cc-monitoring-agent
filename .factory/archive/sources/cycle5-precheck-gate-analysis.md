---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Precheck Gate Failure Taxonomy (Cycle 5 Research)

Comprehensive root cause analysis of 10 consecutive experiment reverts across cycles 2-4. Only 1/10 was a genuine code quality issue (lint regression in exp 022). The other 9 were factory infrastructure failures.

## Gate Failure Frequencies

| Gate | Failure Rate | Experiments Affected |
|---|---|---|
| scope guard (.factory/ dirty files) | 70% (7/10) | 012, 013, 014, 017, 018, 020, 021 |
| score_direction (noise ±0.003) | 40% (4/10) | 016, 017, 020, 023 |
| anti_pattern (text similarity) | 20% (2/10) | 017, 021 |
| factory_effectiveness (death spiral) | 10% (1/10) | 023 |

## Scope Gate

- **Trigger**: Detects uncommitted files in working tree after builder
- **Problem**: CEO session modifies `.factory/events.jsonl`, `.factory/results.tsv`, `.factory/reviews/` during normal ops
- **Fix**: Exclude `.factory/` from scope guard, or run only against `src/` and `tests/`

## Score Direction Gate

- **Trigger**: post-experiment score must be >= pre-experiment
- **Problem**: At eval 1.0, zero margin — any lint warning causes regression. Factory overlay fluctuates ±0.003 from recalculation noise
- **Fix**: Add noise tolerance band (delta >= -0.005 passes)

## Anti-Pattern Gate

- **Trigger**: Text similarity > 0.6 with reverted hypothesis
- **Problem**: Measures feature description similarity, not implementation strategy. "Summary in new file" vs "summary in existing file" flagged as duplicate
- **Fix**: Include implementation metadata in similarity calculation

## Factory Effectiveness Death Spiral

- **Trigger**: Cumulative keep_rate feeds composite score
- **Problem**: Each infra-caused revert lowers keep_rate → lowers composite → guaranteed further reverts
- **Fix**: Exclude infra-caused reverts from keep_rate, or reset per cycle
