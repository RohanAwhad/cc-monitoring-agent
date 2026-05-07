---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (H4 Complete)

## Milestone
H4 (Expand observability) delivered and kept. All 4 improve hypotheses (H1-H4) are now complete.

## Improve Cycle Summary

| Hypothesis | Category | Target Dimension | Status | Verdict |
|---|---|---|---|---|
| H1: Fix 12 mypy strict-mode errors | FIX | type_check (0.4 → 1.0) | Complete | KEEP |
| H2: Configure pytest-cov | FIX | tests/coverage (detection) | Complete | KEEP (retry) |
| H3: Watch mode with Rich Live | EXPLOIT | capability_surface (0.31 → ↑) | Complete | KEEP |
| H4: Expand observability | EXPLOIT | observability (0.5 → 0.8+) | Complete | KEEP |

## Factory Composite Score
- **Current**: 0.517 (eval detection issue persists across all improve experiments)
- **Project eval**: 1.0 (consistently passing)
- **Note**: The factory eval's test/coverage detection and stale caching remain unresolved. All improvements validated by project eval.

## What's Next
The approved improve cycle is complete. Potential next steps from the research backlog:
1. Filtering and sorting flags (`--state`, `--agent`, `--sort`)
2. One-line summary mode for tmux/shell prompt integration
3. State change notifications via macOS osascript

## Project Stats
- **Tests**: 81 (70 unit + 8 watch + 3 integration)
- **Coverage**: 98%
- **Experiments**: 11 total (7 build + 4 improve) + 1 reverted
- **Keep rate**: 91% (10/11)
