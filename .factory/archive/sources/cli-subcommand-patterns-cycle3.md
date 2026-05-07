---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# CLI Subcommand Patterns — Cycle 3 Update

## Finding

Current state on main: flat argparse (no subcommands). PR #7 (watch mode) introduces subcommands but isn't merged.

### Best Practices (2025-2026)

- argparse `add_subparsers()` with `set_defaults(func=handler)` is the zero-dependency pattern. Already used in PR #7.
- Click (38.7% of CLI projects) and Typer offer cleaner decorator syntax but add dependencies.

## Recommendation

Stay with argparse. ccm has 4 subcommands max — the complexity threshold for Click/Typer isn't reached.

## Sources

- [CLI Tools Comparison (2025)](https://dasroot.net/posts/2025/12/building-cli-tools-python-click-typer-argparse/)
- [argparse Subparsers](https://runebook.dev/en/docs/python/library/argparse/argparse.ArgumentParser.add_subparsers)
