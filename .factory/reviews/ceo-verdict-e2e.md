## Cycle 3 Summary — Systemic Blocker Analysis

### Root Cause: Threshold Unachievable
The factory eval composite score is capped at ~0.57 due to three overlay dimensions that cannot be improved from within the project:

1. **tests (0.5, weight 0.15)**: Factory overlay cannot detect pytest despite 88 tests existing. Project eval detects them fine.
2. **coverage (0.5, weight 0.125)**: Factory overlay cannot detect pytest-cov despite 97% coverage. Project eval detects it fine.
3. **research_grounding (0.0, weight 0.08)**: Requires `$FACTORY_VAULT_PATH` to be set — not a project concern.

These three dimensions hold 35.5% of total weight and score at most 0.5 + 0.5 + 0.0 = 1.0/3 = 0.333 weighted average for their share. Even with all other dimensions at 1.0, the max achievable composite is approximately 0.645 — well below the 0.8 threshold.

### Consequence
The precheck gate requires `score >= threshold (0.8)`. Since 0.8 is mathematically impossible, EVERY experiment's precheck will fail with `score_direction: Below threshold`. This makes the factory non-functional for this project.

### Required Fix (Factory Infrastructure)
One of these must happen:
1. Fix factory eval overlay to detect `uv run pytest` and `uv run pytest --cov` (tests/coverage detection)
2. Lower the threshold to match achievable scores (e.g., 0.55)
3. Change precheck logic to check for non-regression rather than absolute threshold

### H4/H5 Not Attempted
Given the systemic blocker, H4 (notifications) and H5 (observability) were not attempted. They would face the same mandatory revert.
