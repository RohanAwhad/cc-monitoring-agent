---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Experiment History Taxonomy (Cycle 5 Research)

## What Worked (Experiments 1-11, 15)

| ID | What | Why It Worked |
|---|---|---|
| 008 | Fix mypy types | Single-file, minimal diff, FIX category |
| 009 | pytest-cov config | Config-only, no new code |
| 010 | Watch mode + subcommands | Build-phase keep (different eval regime) |
| 011 | Observability bundle | Debug-level only, no behavior change |
| 015 | Merge 4 PRs + mypy_path | Operational, precheck skipped |

**Common thread**: Successful experiments either (a) fixed infrastructure/config, (b) were build-phase with different eval rules, or (c) were operational merges. **Zero code-adding feature experiments have been kept since cycle 2 began.**

## Root Cause Taxonomy for Failures (10 experiments)

| Root Cause | Count | Rate |
|---|---|---|
| Scope guard false positives | 7 | 70% |
| score_direction noise | 4 | 40% |
| anti_pattern text similarity | 2 | 20% |
| Lint regression (genuine) | 1 | 10% |
| capability_surface target scaling | 1 | 10% |
| factory_effectiveness death spiral | 1 | 10% |
| Threshold unachievable | 1 | 10% |

**Key insight**: Only 1/10 failures was genuine code quality. The other 9 were factory infrastructure.
