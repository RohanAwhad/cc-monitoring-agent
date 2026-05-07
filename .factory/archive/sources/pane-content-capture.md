---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Pane Content Capture — tmux capture-pane

## Key Findings

- Best approach: `tmux capture-pane -p -t '<target>'` via subprocess.
- `-p` outputs to stdout (no buffer save needed).
- No need for `-S -` (full scrollback) — visible screen is sufficient for activity detection.
- Performance: ~5-10ms per pane.
- `capture-pane` without `-e` strips ANSI escape sequences by default — which is desired behavior.

## Code Pattern

```python
result = subprocess.run(
    ["tmux", "capture-pane", "-p", "-t", f"{session}:{window}.{pane}"],
    capture_output=True, text=True
)
content = result.stdout
```

## libtmux Alternative

`pane.capture_pane()` returns `list[str]`. Cleaner API but adds a pre-1.0 dependency. For MVP, raw subprocess is simpler and sufficient (only 2 tmux commands needed).

## Pitfalls

- Unicode characters (box-drawing, emoji) may appear in content and need handling.
- Pane content varies by terminal size — summary extraction should work on last N lines, not fixed positions.
- OpenCode uses alternate screen buffer (Bubble Tea) — `capture-pane` handles this correctly but scrollback may not be available.
- Race condition: state may change between capture and display (acceptable for MVP snapshot).

## References

- [tmux capture-pane guide](https://tmuxai.dev/tmux-capture-pane/)
- [libtmux docs — Pane Interaction](https://libtmux.git-pull.com/topics/pane_interaction.html)
