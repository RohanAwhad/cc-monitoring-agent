---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 008
verdict: KEEP
score_delta: "+0.0 (factory), +0.483 (project eval)"
date: 2026-05-07
source: factory-archivist
---

# Experiment #008: Fix mypy strict-mode type errors (H1)

## Hypothesis
Fix 12 mypy strict-mode type errors in `src/cc_monitor/analyzer.py` to bring type_check from 0.4 to 1.0. The root cause was functions returning `str` instead of the `AgentState` literal type, and using `str` instead of `Literal["claude", "opencode"]` for `agent_type` parameters.

## Result
**KEEP** — factory composite score 0.517 → 0.517 (delta n/a due to factory eval detection issue), project eval = 1.0

Builder reports eval score 1.0 with mypy strict clean, all 70 tests passing, ruff clean. Factory-level composite score did not update due to a stale eval cache / detection issue — the project's own eval correctly reports 1.0.

## What Changed
- `src/cc_monitor/analyzer.py` — single file, minimal diff:
  - `detect_claude_state()` return type: `str` → `AgentState`
  - `detect_opencode_state()` return type: `str` → `AgentState`
  - `detect_state()` return type: `str` → `AgentState`, parameter `agent_type: str` → `Literal["claude", "opencode"]`
  - `summarize_activity()` parameter `agent_type: str` → `Literal["claude", "opencode"]`
  - Removed `cast()` call in `analyze_sessions()` — no longer needed with proper return types
  - Removed unused `cast` import from `typing`

## Verification
- `mypy --strict src/cc_monitor/` — 0 errors (was 12)
- `pytest tests/ -q` — 70 passed
- `ruff check src/` — all checks passed
- `eval/score.py` — score 1.0

## Analysis
This was a high-leverage FIX: a single-file, 10-line diff resolved all 12 mypy errors. The root cause was the build phase using `str` return types on state detection functions when the data model required `AgentState` (a `Literal` type). The `cast()` workaround in `analyze_sessions` masked the real issue. Tightening the types at the source eliminated both the errors and the cast.

## Links
- Project: cc-monitoring-agent
- Issue: #1
- PR: #2
- Branch: experiment/1-fix-mypy-errors
