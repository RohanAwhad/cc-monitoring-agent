---
tags:
  - factory
  - patterns
source: factory-archivist
---

# Cross-Project Patterns

## Build-phase type workarounds mask strict-mode errors
Discovered in cc-monitoring-agent experiment #008.
Using `cast()` to satisfy type assignments during build can mask real type mismatches that surface under `mypy --strict`. Tightening return types at the source (function signatures) eliminates both the errors and the workaround. When building new modules, prefer correct literal return types from the start rather than broad `str` types with downstream casts.

## Scope violations cause avoidable reverts — expand modifiable scope proactively
Discovered in cc-monitoring-agent experiments #002/#009.
Experiment #002 was reverted solely because `pyproject.toml` was outside the builder's modifiable scope — the code change itself was correct. The retry (#009) succeeded after expanding scope first. When planning config-only experiments that touch build files (pyproject.toml, setup.cfg, etc.), verify the file is in the modifiable scope BEFORE the builder runs. Scope expansion is a low-risk prerequisite that should be done as part of experiment setup, not discovered as a failure mode.

## src-layout projects need source_pkgs, not source, for coverage
Discovered in cc-monitoring-agent experiment #009.
When configuring `[tool.coverage.run]` for a project using Python src-layout (`src/package_name/`), use `source_pkgs = ["package_name"]` instead of `source = ["src/package_name"]`. The `source_pkgs` key tells coverage.py to resolve the package via the import system, which correctly finds it under `src/`. Using `source` with a directory path can fail or report 0% coverage in src-layout projects.

## Subcommand refactoring preserves backward compatibility with default_subparser
Discovered in cc-monitoring-agent experiment #010.
When expanding a single-command CLI to subcommands (e.g., `ccm` → `ccm status` + `ccm watch`), setting a default subparser ensures the bare command (`ccm`) keeps working. This lets you add new capabilities without breaking existing usage. The refactor cost is small — argparse subparsers is stdlib, and the pattern generalizes to future subcommands (filtering, sorting, etc.).

## Observability instrumentation needs no new tests when it's debug-level only
Discovered in cc-monitoring-agent experiment #011.
When adding debug-level logging to existing functions (instrumentation, not behavioral changes), the existing test suite is sufficient — no new tests needed. Debug logging doesn't change function signatures, return values, or side effects. The key constraint: instrumentation must be at debug level only, must not introduce new branching logic, and must not change the public API. If logging adds conditional behavior (e.g., skip processing when log level is X), that's a behavioral change and needs tests.

## Request-level tracing via context-bound IDs enables cross-function log correlation
Discovered in cc-monitoring-agent experiment #011.
Generating a unique scan/request ID at the CLI entry point and binding it to the logger context (e.g., `logger.bind(scan_id=...)`) makes all downstream log entries automatically include the ID. This is especially valuable in continuous-mode tools (watch loops) where multiple scans interleave. The pattern: generate ID at entry, bind once, let the logging framework propagate — no need to pass the ID through every function signature.

## Factory eval systemic regression — src-layout projects scored with system Python
Discovered in cc-monitoring-agent cycle 2 (experiments #012, #013, #014 — all reverted).
The factory eval runs mypy/lint overlay dimensions using system Python, which cannot resolve imports from src-layout projects (`src/package_name/`). Every new Python file adds unresolvable imports, causing `type_check` to drop to 0.0 and triggering false score regressions. The regression magnitude correlates with code addition size: -0.058 (largest), -0.049, -0.032 (smallest). This makes all EXPLOIT/EXPLORE hypotheses that add new Python code unviable for src-layout projects until the factory eval uses `uv run` or project venvs. Workaround: focus on FIX hypotheses or config-only changes that don't add new import surface.

## 0% keep rate signals infrastructure blocker, not code quality issue
Discovered in cc-monitoring-agent cycle 2.
When all experiments in a cycle are reverted with the same failure mode (score_direction precheck) but all pass e2e tests and project eval, the root cause is infrastructure, not code. The correct response is to stop the cycle and fix the eval infrastructure rather than attempting more hypotheses — each attempt wastes builder time for a guaranteed revert. Diagnostic: if project eval = 1.0 but factory precheck fails on score_direction, the overlay dimensions are misconfigured.
