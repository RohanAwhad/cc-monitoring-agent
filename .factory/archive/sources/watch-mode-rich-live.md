---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# Watch Mode with Rich Live Display

From [Rich Live display docs](https://rich.readthedocs.io/en/stable/live.html), [system-monitor-cli (PyPI)](https://pypi.org/project/system-monitor-cli/), [terminal monitoring guide (Medium)](https://medium.com/@cumulus13/building-beautiful-terminal-based-network-monitoring-tools-in-python-6a036514097a).

## Key Findings

- Rich `Live` context manager provides flicker-free terminal refresh
- No threading needed — discover+analyze takes ~50ms total, well within a 2s poll interval
- `refresh_per_second` parameter controls render rate independent of data collection rate
- Graceful exit on `KeyboardInterrupt`
- Rich `Live` is already available since `rich` is a dependency — no new deps needed

## Reference Implementation

```python
with Live(table, refresh_per_second=4) as live:
    while True:
        sessions = discover_sessions()
        analyze_sessions(sessions)
        live.update(build_table(sessions))
        time.sleep(interval)
```

- `--interval` flag for configurable poll rate (default 2s)
- Highest-impact feature for a monitoring tool — continuous observation is the core use case
