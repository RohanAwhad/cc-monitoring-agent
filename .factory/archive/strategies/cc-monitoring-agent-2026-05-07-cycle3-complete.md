---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 3 Complete)

## Cycle 3 Final Summary

**5 experiments run, 1 kept, 3 reverted, 1 error. Post-H1 keep rate: 0%.**

The cycle confirmed a systemic blocker: the factory eval threshold (0.800) is mathematically unachievable for this project. Maximum possible composite score is approximately 0.645.

## What Happened

### H1: Fix eval blocker + merge PRs (KEEP)
- Added `mypy_path = "src"` to pyproject.toml
- Merged 4 open PRs (#2, #5, #7, #9) to main in dependency order
- Project eval 1.0, factory composite 0.537 (marginal drop from 0.539)
- Operational prerequisite — unblocked subsequent experiments

### H2: Filtering/sorting flags (REVERT x2)
- Attempt 1: Score -0.018 (type_check overlay regression from new imports)
- Attempt 2: Score -0.001 + anti_pattern (factory won't allow retry of same failing approach)
- Code was functionally correct both times

### H3: Summary mode (ERROR + REVERT)
- Attempt 1: PR included dirty .factory/ files — builder hygiene issue
- Attempt 2: Score 0.572 vs threshold 0.800 — threshold mathematically impossible

## Systemic Blocker Analysis

The factory composite is calculated across multiple dimensions. Three overlay dimensions are permanently broken for this project:

| Dimension | Value | Why Broken |
|---|---|---|
| tests | 0.5 | Factory eval doesn't detect pytest suite |
| coverage | 0.5 | Factory eval doesn't detect coverage config |
| research_grounding | 0.0 | Dimension not scored for this project type |

These broken dimensions contribute to a ceiling of ~0.645, making the 0.800 precheck threshold impossible to pass. No code change can fix this — it requires factory eval infrastructure changes.

## Cross-Cycle Retrospective

| Cycle | Experiments | Keep Rate | Root Cause of Failures |
|---|---|---|---|
| Build | 7 | 100% (7/7) | N/A |
| Cycle 1 | 5 | 80% (4/5) | 1 scope violation (config-only) |
| Cycle 2 | 3 | 0% (0/3) | Systemic: system Python can't resolve src-layout imports |
| Cycle 3 | 5 | 20% (1/5) | Systemic: overlay dimensions cap max score below threshold |

**Total project: 20 experiments, 11 kept, 8 reverted, 1 error (55% overall keep rate)**

## Project State at Cycle 3 End

- **Project eval**: 1.0 (perfect)
- **Factory composite**: 0.537
- **Tests**: 81 passing
- **Coverage**: 97%
- **mypy (project)**: 0 errors
- **Features delivered**: scan, watch, structured logging, observability tracing
- **Features blocked**: filtering/sorting, summary mode, notifications

## Recommendation

This project is **functionally complete** and should be marked as such in the factory. Further improvement cycles will produce the same outcome (correct code → revert) until the factory eval:
1. Uses `uv run` or project venvs for overlay dimensions (type_check, tests, coverage)
2. Properly detects pytest suites in src-layout projects
3. Either scores or excludes research_grounding for CLI tool projects
4. Adjusts the precheck threshold to be achievable given dimension constraints
