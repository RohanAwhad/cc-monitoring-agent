# Builder Agent Output

- **timestamp:** 2026-05-07T18:17:55Z
- **exit_code:** 0

---

PR created: https://github.com/RohanAwhad/cc-monitoring-agent/pull/24

**Summary:**
- Added `_format_summary()` and `_run_summary()` to `src/cc_monitor/cli.py` with a `summary` subparser
- Output format: `3 agents: 2 working, 1 idle` — plain text, no ANSI, no trailing newline
- `0 agents` for empty case
- Added `tests/test_summary.py` with 7 tests covering all state combinations
- All 88 tests pass, 97.53% coverage, ruff clean
