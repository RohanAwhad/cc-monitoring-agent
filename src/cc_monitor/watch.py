from __future__ import annotations

import time

from loguru import logger
from rich.live import Live
from rich.table import Table

from cc_monitor.analyzer import analyze_sessions
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import STATE_STYLES
from cc_monitor.models import AgentSession


def _build_table(sessions: list[AgentSession]) -> Table:
    logger.debug("_build_table called with {} sessions", len(sessions))
    table = Table(title="Claude Code Monitor (watch mode)")
    table.add_column("Tmux Target")
    table.add_column("Agent")
    table.add_column("State")
    table.add_column("Summary")

    for s in sessions:
        style = STATE_STYLES.get(s.state, "")
        table.add_row(
            s.tmux_target,
            s.agent_type,
            f"[{style}]{s.state}[/{style}]" if style else s.state,
            s.summary,
        )

    return table


def watch_loop(interval: float = 2.0) -> None:
    logger.info("starting watch mode (interval={:.1f}s)", interval)
    with Live(_build_table([]), refresh_per_second=1) as live:
        while True:
            sessions = discover_sessions()
            sessions = analyze_sessions(sessions)
            live.update(_build_table(sessions))
            time.sleep(interval)
