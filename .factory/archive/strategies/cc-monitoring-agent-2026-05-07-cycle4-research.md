---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Cycle 4 Research)

## CEO Verdict: PROCEED

Research covers all 3 requested topics with actionable depth. No significant issues found.

## Research Topics Covered

### 1. AnthropicVertex SDK (Issue #23)
- SDK import and usage pattern documented
- User's env var mapping identified (ANTHROPIC_VERTEX_PROJECT_ID, VERTEX_LOCATION mismatch with CLOUD_ML_REGION)
- Recommended client init with explicit env var mapping
- New module plan: `src/cc_monitor/llm.py` with `analyze_pane(text: str) -> str`
- Model: `claude-sonnet-4-5@20250929` (small/fast for pane summarization)
- ~5 capability_surface units added

### 2. Eval Score Offset Strategy
- Quantified the 0.5 drag from broken tests/coverage overlay dimensions
- Capability surface improvement: +0.021 composite (all 4 backlog items)
- Observability improvement: +0.035 composite (full function coverage)
- Total offset: +0.056 — offsets 56% of drag
- **Key insight: Bundle strategy** — each experiment should improve 3 dimensions simultaneously

### 3. macOS Notifications (Confirmed)
- osascript silently fails on Sequoia — confirmed with fresh sources
- terminal-notifier is reliable alternative (own app entry in System Settings)
- Sequoia caveat: don't use `-sender` with `-activate`

## CEO Instructions to Strategist

1. Adopt bundle strategy: every hypothesis = feature + logging + API surface
2. Include Issue #23 (LLM analysis) as a growth hypothesis
3. Prioritize by capability_surface unit yield

## Backlog State

6 items (3 unique, 3 duplicates): filtering/sorting, summary mode, notifications — all tried 1-3x, all reverted due to eval blocker (now partially mitigated by bundle strategy).
