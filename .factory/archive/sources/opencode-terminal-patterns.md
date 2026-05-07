---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# OpenCode Terminal Patterns

## Idle / Waiting for Input

Bottom bar pattern:
```
  |
  |
  |  Auto-Accept . Claude Opus 4.6 Vertex (Anthropic) . max
  -=============================
                                    25.2K (3%) . $0.19  ctrl+p commands
```

Key markers: `Auto-Accept` or model name in status bar, `ctrl+p commands` at bottom right.

## Active Processing

```
  Auto-Accept . Claude Opus 4.6 . 3m 53s
```

Key marker: timer duration visible (e.g., `3m 53s`), indicates active processing.

## Waiting for User Input

The input area shows `|` (vertical bar) with an empty input line.

## State Detection Heuristics

**Waiting for input:**
- Bottom area has empty `|` input field
- Status bar shows model name but no active timer

**Actively working:**
- Status bar shows active timer (e.g., `. 3m 53s`)
- Recent content shows tool call output

## References

- [OpenCode GitHub](https://github.com/opencode-ai/opencode)
- [OpenCode docs](https://opencode.ai/docs/)
