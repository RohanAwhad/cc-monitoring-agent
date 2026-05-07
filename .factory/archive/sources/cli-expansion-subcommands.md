---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# CLI Feature Expansion Patterns (Subcommands)

From [argparse docs](https://docs.python.org/3/library/argparse.html), [Real Python guide](https://realpython.com/command-line-interfaces-python-argparse/).

## Key Findings

Proposed subcommand structure:
- `ccm status` — current behavior (list all sessions)
- `ccm watch` — continuous polling with live refresh
- `ccm attach <target>` — shortcut to `tmux attach -t`
- `ccm summary` — compact one-line output for shell prompts

### Implementation Pattern

`set_defaults(func=handler)` on each subparser, dispatch via `args.func(args)` in main.

### Backward Compatibility

Bare `ccm` (no subcommand) should behave as `ccm status`. Achieved by setting `default` on the subparser or checking `hasattr(args, 'func')`.

### Additional Flags

- `--state working|idle|needs_input` — filter by state
- `--agent claude|opencode` — filter by agent type
- `--sort state|agent|session` — sort output
- Implementation: pure Python filtering/sorting on `list[AgentSession]` before display
