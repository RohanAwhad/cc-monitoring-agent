---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 17
verdict: revert
score_delta: -0.0002
date: 2026-05-07
source: factory-archivist
---

# Experiment #023 (ID 17): LLM-powered pane analysis via AnthropicVertex (Cycle 4 H4)

## Hypothesis
Add LLM-powered pane analysis using AnthropicVertex SDK. Inline implementation in `analyzer.py` (no new modules), `--llm` flag for opt-in, `anthropic` dependency added.

## Result
**REVERT** — score changed by -0.0002 (noise-level regression)

## What Changed
- **Modified `src/cc_monitor/analyzer.py`**: added `analyze_pane_llm()` function using AnthropicVertex client
- **Modified `src/cc_monitor/cli.py`**: added `--llm` flag
- **Added dependency**: `anthropic[vertex]` in pyproject.toml
- **5 new tests** for LLM analysis function

## Root Cause of Failure
Factory effectiveness death spiral. The -0.0002 delta is noise-level (statistically insignificant), but the `factory_effectiveness` dimension in the composite score accounts for cumulative keep rate. Each consecutive revert in this cycle lowered the keep_rate, which lowered the composite, which caused the next experiment to also fail the score_direction precheck. By experiment 17, the keep_rate had dropped enough that even a neutral-score experiment would be reverted.

## Key Insight
**Death spiral pattern**: revert → lower keep_rate → lower composite → next experiment starts from lower baseline → even smaller regressions trigger revert → keep_rate drops further. This is a self-reinforcing feedback loop that makes recovery impossible within a single cycle once the initial reverts occur.

## Links
- Project: cc-monitoring-agent
- Issue: #31
- PR: (created but reverted)
