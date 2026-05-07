---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# mypy Strict Mode for src Layout

From [mypy docs](https://mypy.readthedocs.io/en/stable/config_file.html) and [pydevtools guide](https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/).

## Key Findings

- `packages = ["cc_monitor"]` lets you run `mypy` without path args
- `warn_unreachable = true` is NOT included in `--strict` but catches dead code paths
- Test overrides (`disallow_untyped_defs = false`) are standard practice
- subprocess.Run in strict mode: always pass `text=True` as literal (not variable), annotate result types explicitly. The heavily overloaded type stubs in typeshed for subprocess.run are the most common source of strict-mode type errors in CLI tools.

## Recommended Configuration

```toml
[tool.mypy]
strict = true
packages = ["cc_monitor"]
warn_unreachable = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```
