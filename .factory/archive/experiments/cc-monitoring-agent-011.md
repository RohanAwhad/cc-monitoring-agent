---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 011
verdict: KEEP
score_delta: "+0.0 (factory composite unchanged due to eval detection issue)"
date: 2026-05-07
source: factory-archivist
---

# Experiment #011: Expand observability — logging coverage & request tracing (H4)

## Hypothesis
Add debug logging to uninstrumented functions and implement request-level tracing with `scan_id` correlation. This targets the `observability` eval dimension (currently 0.5, function_coverage=0.33, structured_logging=False) by expanding logging coverage from ~33% to 80%+ and adding per-scan traceability.

## Result
**KEEP** — factory composite score 0.517 → 0.517 (delta +0.0, eval detection issue persists). Project eval 1.0. All 70 tests pass. CEO verdict: KEEP.

## What Changed
- `src/cc_monitor/logging.py` — Added `serialize=True` to file sink for structured JSON output (machine-parseable logs)
- `src/cc_monitor/cli.py` — Generate unique `scan_id` via `uuid4().hex[:8]` at CLI entry; bind to loguru context via `logger.bind(scan_id=...)`. Added debug logging for CLI args, discovery results, and output rendering
- `src/cc_monitor/display.py` — Added debug logging to `display_results()`: entry point, empty state detection, and per-row session data
- `src/cc_monitor/models.py` — Added `__post_init__` debug log on `AgentSession` creation with session metadata

## Verification
- 70 tests pass (no new tests — observability changes are instrumentation-only)
- Project eval: 1.0
- CEO review: KEEP
- Structured JSON logs validated in file sink

## Analysis
H4 completes the improve cycle's observability goal. The key design decisions:

1. **scan_id tracing**: Each `ccm status` or `ccm watch` invocation generates a unique 8-char hex ID, bound to loguru context. This makes it possible to correlate all log entries from a single scan — critical for debugging when watch mode runs continuous scans.

2. **Structured JSON file sink**: Adding `serialize=True` to the file sink means log files are machine-parseable (one JSON object per line), enabling downstream analysis tools without changing the human-readable stderr output.

3. **No new tests**: This was deliberate — observability changes are pure instrumentation (debug-level logging), with no behavioral changes to the public API. Existing tests continue to pass because debug logging doesn't affect function outputs.

Growth target: `observability` (0.5 → expected 0.8+ with function_coverage increase and structured logging flag).

## Links
- Project: cc-monitoring-agent
- Issue: #8
- PR: #9
- Branch: experiment/5-observability
- Commit: 73d311d
