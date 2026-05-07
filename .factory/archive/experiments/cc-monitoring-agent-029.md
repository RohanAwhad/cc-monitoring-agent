---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 23
verdict: pending
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #029 (ID 23): Gemini CLI and Codex CLI detection (Cycle 7 H1)

## Hypothesis
Add Gemini CLI (`gemini` command) and Codex CLI (`codex` command) detection to the discovery and analyzer pipeline. Extends agent_type Literal, adds prompt-based state detection, and wires into existing dispatch functions.

## Implementation

### Files Changed (source only)
- **`src/cc_monitor/models.py`**: Extended `AgentSession.agent_type` Literal from `["claude", "opencode"]` to `["claude", "opencode", "gemini", "codex"]`
- **`src/cc_monitor/discovery.py`**: Added `PaneClass` Literal with `"gemini"` and `"codex"` entries; `classify_pane()` now matches `gemini` and `codex` commands; `discover_sessions()` handles new classifications in the same branch as `opencode` (no new code path, collapsed via `in ("opencode", "gemini", "codex")`)
- **`src/cc_monitor/analyzer.py`**: Added `_GEMINI_PROMPT_RE` and `_CODEX_PROMPT_RE` regex patterns; added `detect_gemini_state()`, `detect_codex_state()`, `summarize_gemini_activity()`, `summarize_codex_activity()` — all follow exact patterns of existing opencode functions; wired into `detect_state()` and `summarize_activity()` dispatchers

### Tests Added (15 new, 99 total)
- **`tests/test_analyzer.py`**: `TestDetectGeminiState` (3 tests), `TestDetectCodexState` (3 tests), `TestDetectStateGeminiCodex` (2 tests), `TestSummarizeGeminiActivity` (3 tests), `TestSummarizeCodexActivity` (3 tests)
- **`tests/test_discovery.py`**: `test_gemini_pane`, `test_codex_pane`, `test_gemini`/`test_codex` in classify, updated `test_discovers_all_agent_types` with 4-type assertion
- **`tests/test_basic.py`**: Minor formatting cleanup (no functional change)

### Architecture Observations
- **Pattern-compliant**: Follows the exact same command-based classification → state detection → summarization pipeline established for claude and opencode
- **No new files**: All code embedded in existing modules (continues the no-new-files strategy from cycle 5+)
- **No new dependencies**: Pure regex-based detection, no external packages
- **Prompt-based state detection**: `gemini>` and `codex>` prompt patterns detected in bottom 5 lines of pane content, consistent with opencode's approach
- **Display works out of the box**: `agent_type` is rendered as-is in the Rich table, no display changes needed

## CEO Verdict
**PROCEED** — Clean, well-scoped implementation. Follows existing patterns exactly. 15 new tests. No new files. No scope creep.

## Links
- Project: cc-monitoring-agent
- PR: #44
- Issue: #43
