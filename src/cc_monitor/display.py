from __future__ import annotations

from loguru import logger
from rich.console import Console
from rich.table import Table

from cc_monitor.models import AgentSession

STATE_STYLES: dict[str, str] = {
    "idle": "green",
    "working": "yellow",
    "needs_input": "bold red",
}


def display_results(sessions: list[AgentSession]) -> None:
    logger.debug("display_results called with {} sessions", len(sessions))
    console = Console()

    if not sessions:
        logger.debug("no sessions to display")
        console.print("No agent sessions found in tmux.")
        return

    table = Table()
    table.add_column("Tmux Target")
    table.add_column("Agent")
    table.add_column("State")
    table.add_column("Summary")

    for s in sessions:
        style = STATE_STYLES.get(s.state, "")
        logger.debug("rendering row: target={} state={}", s.tmux_target, s.state)
        table.add_row(
            s.tmux_target,
            s.agent_type,
            f"[{style}]{s.state}[/{style}]" if style else s.state,
            s.summary,
        )

    console.print(table)


def format_summary(sessions: list[AgentSession]) -> str:
    logger.debug("format_summary called with {} sessions", len(sessions))
    total = len(sessions)
    if total == 0:
        logger.debug("no sessions, returning zero summary")
        return "0 agents"

    from collections import Counter

    counts: Counter[str] = Counter(s.state for s in sessions)
    logger.debug("state counts: {}", dict(counts))
    parts: list[str] = []
    for state in ("working", "idle", "needs_input"):
        n = counts.get(state, 0)
        if n > 0:
            parts.append(f"{n} {state}")

    label = "agent" if total == 1 else "agents"
    return f"{total} {label}: {', '.join(parts)}"
