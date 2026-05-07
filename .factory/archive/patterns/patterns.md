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
