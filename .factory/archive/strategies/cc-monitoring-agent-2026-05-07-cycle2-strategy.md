---
tags:
  - factory
  - strategy
  - cc-monitoring-agent
date: 2026-05-07
source: factory-archivist
---

# Strategy: cc-monitoring-agent — 2026-05-07 (Improve Cycle 2)

## CEO Verdict: PROCEED

All 3 hypotheses approved. Priority order: H1, H2, H3.

## Strategy Summary

Cycle 2 clears all 3 remaining backlog items, all targeting **capability_surface** (0.31 — weakest dimension). No new items added; pure backlog clearing.

### Hypotheses

| # | Hypothesis | Category | Target | Priority | Branch Base |
|---|---|---|---|---|---|
| H1 | Filtering & sorting flags (`--state`, `--agent`, `--sort`) | EXPLOIT | capability_surface | high | experiment/4-watch-mode (PR #7) |
| H2 | One-line summary mode (`ccm summary` / `--oneline`) | EXPLORE | capability_surface | high | experiment/4-watch-mode (PR #7) |
| H3 | State change notifications (`ccm watch --notify`) | EXPLORE | capability_surface | medium | experiment/4-watch-mode (PR #7) |

### Key Decisions

1. **All branches from experiment/4-watch-mode** — PR #7 introduced subcommand architecture (`add_subparsers()`) that all 3 hypotheses depend on. PRs target experiment/4-watch-mode, not main.
2. **Merge prerequisite** — Cycle 1 PRs (#2, #5, #7, #9) must merge before cycle 2 branches are created. All 4 were KEEP-verdicted.
3. **Same growth dimension** — All 3 target capability_surface. experiment_diversity may dip, but backlog priority overrides.
4. **Backlog cleanup needed** — Backlog has duplicates (3 items x2 = 6 entries). Needs cleanup after this cycle.

### Expected Impact

- capability_surface: 0.31 → ~0.38 (H1) / ~0.37 (H2) / ~0.36 (H3)
- Combined potential: significant capability_surface growth through new CLI features

### Anti-patterns to Avoid

- Don't re-implement cycle 1 features (watch mode, mypy, pytest-cov, observability)
- Don't use libtmux — subprocess confirmed sufficient
- Don't add click/typer — argparse subcommands from PR #7 are enough
- Don't add daemon mode — watch mode + notifications covers continuous monitoring
- `detect_state` returns `str` not `Literal` — use `cast()` matching existing pattern
- Factory eval overlay dimensions use system Python not `uv run` — score improvements depend on factory-level fixes

### Observations

- Current composite score: 0.539 (main branch)
- Factory composite is stale — project eval passes all dimensions at 1.0
- 4 unmerged cycle 1 PRs block score improvement on main
- 12 experiments total (11 kept, 1 reverted) across build + cycle 1
