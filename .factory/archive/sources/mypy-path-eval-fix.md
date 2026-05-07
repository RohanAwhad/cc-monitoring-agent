---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Factory Eval Blocker Fix — mypy_path for src-layout

## Finding

The systemic eval blocker (system Python can't resolve src-layout imports) has a project-level workaround:

```toml
[tool.mypy]
mypy_path = "src"
```

This tells mypy where to find packages even when not running from a virtualenv. If the factory eval runs `python -m mypy src/` with system Python, setting `mypy_path = "src"` in pyproject.toml should resolve the import failures.

**Alternative**: `mypy_path = "$MYPY_CONFIG_FILE_DIR/src"` for config-relative resolution.

## Impact

This is the highest-priority fix — unblocking the eval infrastructure makes all 3 reverted backlog items (filtering, summary, notifications) viable again.

## Sources

- [mypy config docs](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy running imports](https://mypy.readthedocs.io/en/stable/running_mypy.html)
- [src-layout packaging](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
