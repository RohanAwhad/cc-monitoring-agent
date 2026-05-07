---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Improve Cycle 1 Complete)

## Milestone
Improve Cycle 1 complete. All 4 hypotheses (H1-H4) delivered and kept. 5 experiments total, 4 kept, 1 reverted. The project entered improve mode after a 7-phase build that delivered 70 tests and a working CLI tool.

## Cycle Stats

- **Experiments**: 5 (factory IDs 1-5, archive IDs 008-011 + revert-002)
- **Kept**: 4, **Reverted**: 1
- **Keep rate**: 80%
- **Score movement**: Factory composite stuck at 0.517 (eval detection issue), project eval stable at 1.0
- **Test growth**: 70 → 81 tests (+11)
- **Coverage**: 0% → 98% (pytest-cov added in H2)

## Hypotheses Delivered

| # | Hypothesis | Category | Target | Verdict | Impact |
|---|---|---|---|---|---|
| H1 | Fix 12 mypy strict-mode errors | FIX | type_check | KEEP | 12 errors → 0, single-file 10-line diff |
| H2 | Configure pytest-cov (attempt 1) | EXPLOIT | tests/coverage | REVERT | Scope violation: pyproject.toml read-only |
| H2 | Configure pytest-cov (retry) | EXPLOIT | tests/coverage | KEEP | 98% coverage, src-layout source_pkgs config |
| H3 | Watch mode (Rich Live) | EXPLOIT | capability_surface | KEEP | New module, subcommand, 8 new tests |
| H4 | Observability expansion | EXPLOIT | observability | KEEP | scan_id tracing, structured JSON, 33%→80%+ function coverage |

## Key Decisions

1. **FIX before EXPLOIT**: H1 (mypy fix) was prioritized first to clear a known defect before adding new capabilities. Correct decision — the fix was a 10-line diff that unblocked clean strict-mode CI.

2. **Scope expansion before retry**: After the H2 revert, the CEO expanded `pyproject.toml` into the modifiable scope before retrying. This prevented a second revert and established the pattern of proactive scope checks.

3. **Subcommand refactor in H3**: Rather than adding watch as a flag (`ccm --watch`), the builder refactored CLI to argparse subcommands (`ccm status`, `ccm watch`). This paid forward — future subcommands (filtering, summary) can slot in cleanly.

4. **No new tests for H4 (observability)**: Debug-level instrumentation doesn't change public API behavior, so existing tests sufficed. This was a deliberate tradeoff, not an oversight.

## Factory Eval Issue

The factory composite score (0.517) never moved during this cycle because `last_eval.json` was stale. It still reports:
- `type_check: 0.4` (fixed in H1, now 0 errors)
- `tests: 0.5` (detected in H2, now 81 tests with 98% coverage)
- `coverage: 0.5` (detected in H2)
- `capability_surface: 0.3143` (should have grown with H3's new module)
- `observability: 0.5` (improved in H4, structured logging + scan_id tracing)

The project's own eval (`eval/score.py`) correctly returns 1.0. The divergence is a factory infrastructure issue, not a project quality issue.

## Patterns Discovered

1. **Build-phase type workarounds mask strict-mode errors** — `cast()` hid real type mismatches (H1)
2. **Scope violations cause avoidable reverts** — check modifiable scope proactively (H2)
3. **src-layout needs source_pkgs, not source** — coverage.py config key difference (H2)
4. **Subcommand refactoring preserves backward compat with default_subparser** — argparse pattern (H3)
5. **Observability instrumentation needs no new tests when debug-level only** — instrumentation ≠ behavioral change (H4)
6. **Request-level tracing via context-bound IDs** — generate at entry, bind once, auto-propagate (H4)

## Remaining Growth Targets (for Cycle 2)

From the research phase, these remain unimplemented:
- **Filtering and sorting flags** (`--state`, `--agent`, `--sort`) — EXPLOIT, capability_surface
- **One-line summary mode** — EXPLORE, tmux status bar integration
- **State change notifications** — EXPLORE, macOS osascript

Additionally, the factory eval detection issue should be investigated as a FIX priority.
