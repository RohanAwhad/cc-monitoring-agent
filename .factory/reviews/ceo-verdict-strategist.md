## CEO Review: Strategist Agent
- **Verdict:** PROCEED
- **Rationale:** Two well-scoped growth hypotheses targeting capability_surface. Both follow the validated no-new-files pattern. H1 (attach) is low-effort/high-value. H2 (costs) is the unique differentiator. Both are pure additions — no regression risk to eval 1.0.
- **Issues found:** None
- **Instructions for next step:**

PLAN APPROVED

**Approved hypotheses in priority order:**
1. **H1:** `ccm attach` subcommand — add to cli.py, ~20 lines, 5+ tests
2. **H2:** Token/cost estimation via `--costs` flag — add to analyzer.py + cli.py, 6+ tests

**Notes for Builder:**
- Follow no-new-files pattern: add functions to existing modules only
- Run `ruff format` and `ruff check` before committing
- Run `uv run mypy src/ --strict` to verify type safety
- Each hypothesis is a separate experiment branch
- Do NOT modify eval/score.py or .factory/
