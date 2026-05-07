---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — Cycle 7 (2026-05-07)

## CEO Verdict: PROCEED

Two well-scoped growth hypotheses approved. Both follow the validated no-new-files pattern. Budget satisfied: 2 growth hypotheses (min 2), 2 new backlog items deferred (max 2). Titles distinct from prior reverted experiments — no anti_pattern risk.

## Approved Hypotheses

### H1: Gemini CLI + Codex CLI Detection (Priority: HIGH)
- **Category:** EXPLORE
- **Growth dimension:** capability_surface (0.31 → 0.37 projected)
- **What:** Extend `discovery.py` to detect Gemini CLI (`gemini`) and Codex CLI (`codex`) sessions in tmux panes. Add classification patterns to pane classifier. Extend `AgentSession.agent_type` in `models.py` with `"gemini"` and `"codex"` literals. Update `analyzer.py` state detection for Gemini/Codex terminal output patterns. Add 8+ tests. No new files.
- **Why:** CEO's #1 priority. TmuxCC already supports 4 agent types — this closes the competitive gap and strengthens ccm's "works with any agent" differentiator. Adds new public functions and agent type constants to capability_surface count.
- **Expected impact:** capability_surface 0.31 → 0.37 (+4 public fns, +2 agent type constants), experiment_diversity +0.02

### H2: Observability Function Coverage 32% → 60%+ (Priority: HIGH)
- **Category:** EXPLOIT
- **Growth dimension:** observability (0.53 → 0.72 projected)
- **What:** Add `logger.debug()` calls to all uninstrumented functions across `discovery.py`, `analyzer.py`, `cli.py`, `display.py`, `watch.py`, and `models.py`. Current: 7/22 functions (32%). Target: 14+/22 (>60%). Add request tracing via `contextvars` for scan_id propagation. No new files.
- **Why:** CEO's #3 priority. Observability at 0.53 is near the 0.5 action threshold. Debug logging is zero-risk (no behavioral change). Historically high keep rate for observability experiments.
- **Expected impact:** observability 0.53 → 0.72 (fn_coverage 0.32 → 0.64, request_tracing detected)

## Deferred Backlog Items
1. Fix 2 remaining mypy errors in factory overlay detection (type_check 0.9 → 1.0) — CEO priority #4
2. Add pending approval detection: enhance `needs_input` state to detect and count pending approval prompts — CEO priority #2

## Builder Notes
- Follow no-new-files pattern: add functions to existing modules only
- Run `ruff format` and `ruff check` before committing (keep lines <88 chars)
- Run `uv run mypy src/ --strict` to verify type safety
- Each hypothesis is a separate experiment branch
- Do NOT modify eval/score.py or .factory/
- For H1: research actual terminal patterns for Gemini CLI and Codex CLI before implementing detection
- For H2: use loguru `{}` formatting, not f-strings in log calls

## Context
- **Factory composite:** 0.577 (project eval 1.0, factory overlay drags score)
- **Weakest dimensions:** capability_surface 0.31, observability 0.53, tests 0.50, coverage 0.50
- **Recent streak:** 5 consecutive keeps (cycles 5-6), 100% keep rate
- **Total experiments:** 22 run, 10 kept, 11 reverted, 1 error
- **Competitive landscape:** 10+ new competitors. TmuxCC supports 4 agent types. ccm differentiates via zero-config + agent-agnostic.
