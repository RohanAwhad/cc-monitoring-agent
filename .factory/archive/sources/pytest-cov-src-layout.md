---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# pytest-cov Configuration for src Layout

From [pytest-cov docs](https://pytest-cov.readthedocs.io/en/latest/config.html), [Scientific Python guide](https://learn.scientific-python.org/development/guides/coverage/), [Coverage.py config reference](https://coverage.readthedocs.io/en/latest/config.html).

## Key Findings

- `source_pkgs = ["cc_monitor"]` is essential for src-layout projects — using `source = ["src"]` measures the wrong paths
- Coverage.py reads from `pyproject.toml` natively on Python 3.11+
- `fail_under = 80` is a reasonable threshold given 70 tests for ~200 LOC

## Recommended Configuration

```toml
[tool.pytest.ini_options]
addopts = "--cov=cc_monitor --cov-config=pyproject.toml --cov-report=term-missing"

[tool.coverage.run]
source_pkgs = ["cc_monitor"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

Requires adding `pytest-cov` to dev dependencies.
