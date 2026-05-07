---
tags:
  - factory
  - experiment
  - cc-monitoring-agent
project: cc-monitoring-agent
experiment_id: 12
verdict: error
score_delta: 0.0
date: 2026-05-07
source: factory-archivist
---

# Experiment #12: Add one-line summary mode (ccm summary) — ERROR

## Hypothesis
Add `ccm summary` subcommand for one-line tmux status bar integration. Output a single-line summary of agent states suitable for embedding in tmux status-right or shell prompts. Targeting capability_surface dimension.

## Result
**ERROR** — PR included dirty `.factory/` files. Experiment closed and retried as #13.

## What Changed
- Summary mode implementation was correct
- Builder created PR but it included uncommitted `.factory/` state files (events.jsonl, results.tsv, reviews)
- PR was closed without merge; experiment retried with clean working tree

## Root Cause
The builder's working directory had dirty `.factory/` files from prior experiment operations. When the builder staged changes for the PR, it picked up these unrelated files. This is a builder hygiene issue, not a code quality issue.

## Key Observations
1. Factory state files (.factory/) should be in .gitignore or the builder should explicitly exclude them
2. The code implementation itself was not evaluated — the error was purely operational
3. This consumed one experiment slot without providing signal about the hypothesis

## Links
- Project: cc-monitoring-agent
- Issue: #20
