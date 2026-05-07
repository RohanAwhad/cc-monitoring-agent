# Factory Configuration

## Goal

A CLI tool that monitors all Claude Code and OpenCode sessions running in tmux, showing what each agent is doing, whether it needs user input, and the tmux coordinates to jump there.

## Scope

### Modifiable

- src/**/*.py
- tests/**/*.py
- pyproject.toml

### Read-only

- README.md
- eval/score.py

## Guards

- Do not delete or overwrite existing tests
- Do not modify files outside the declared scope
- Do not introduce secrets or credentials into the repository

## Eval

### Command

```bash
python eval/score.py
```

### Threshold

0.8

## Target Branch

main

## Smoke Test

```bash
uv run ccm --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'sessions' in d; print(f'OK: {len(d[\"sessions\"])} sessions')"
```

## Constraints

- Prefer small, incremental changes over large rewrites
- Each change should be accompanied by at least one test
- Follow the existing code style and conventions
