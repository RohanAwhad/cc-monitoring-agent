---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Rich Live vs Textual for TUI Features

## Finding

- **Rich `Live` + `Table`**: Sufficient for watch mode (flicker-free refresh, no threading needed). Does NOT support interactive filtering/sorting natively.
- **Textual `DataTable`**: Full interactive table with cursor modes (cell/row/column/none), programmatic `sort(*columns, key=...)`, vim-style navigation. No built-in filtering API — must be implemented via remove/re-add rows. Adds `textual` dependency.

## Recommendation

Stay with Rich `Live` + pre-filter approach. Filtering via CLI flags (`--state`, `--agent`) is simpler and more composable (pipes, scripts) than interactive TUI filtering. Sorting via `--sort` flag with Python `sorted()` on `list[AgentSession]` is trivial. No new dependency needed.

## Sources

- [Textual DataTable](https://textual.textualize.io/widgets/data_table/)
- [Rich Live Display docs](https://rich.readthedocs.io/en/latest/live.html)
