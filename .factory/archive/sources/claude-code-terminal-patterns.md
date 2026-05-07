---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Claude Code Terminal Patterns

## Idle / Waiting for Input

```
> 
---
  [%%%%%%%%] $1.430
  >> bypass permissions on (shift+tab to cycle)
```

Key markers: `>` prompt character, cost indicator `$X.XX`, `>>` permission mode indicator.

## Active Tool Use

```
* Bash(echo "test")
|- (No content)
```

Key markers: `*` (tool call indicator), tool name in format `ToolName(args)`.

## Thinking / Processing

Shows inline progress: "still thinking", "thinking more", "almost done thinking".

## Completion Marker

```
* Worked for 9m 26s
```
or
```
* Cooked for 9m 2s
```

## Recap Section

```
* recap: Building a writing assistance webapp...
```

## State Detection Heuristics

**Waiting for input:**
- Bottom of pane contains `>` (the prompt character)
- Bottom section has the cost bar `[%%%%...] $X.XX`
- No active tool call indicator (`*`) in the last ~10 lines

**Needs permission:**
- Contains permission prompt patterns (yes/no dialog)

**Actively working:**
- Contains `*` tool markers in recent output
- Contains thinking indicators
- No `>` prompt visible at bottom

## References

- [Under the hood of Claude Code](https://pierce.dev/notes/under-the-hood-of-claude-code)
- [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)
