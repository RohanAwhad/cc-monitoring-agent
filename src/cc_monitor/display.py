from __future__ import annotations

from collections import Counter

from rich.console import Console
from rich.table import Table

from cc_monitor.models import AgentSession

STATE_STYLES: dict[str, str] = {
    "idle": "green",
    "working": "yellow",
    "needs_input": "bold red",
}

COMPACT_ICONS: dict[str, str] = {
    "working": "⚡",
    "idle": "🕐",
    "needs_input": "❗",
}


def format_summary(sessions: list[AgentSession]) -> str:
    total = len(sessions)
    if total == 0:
        return "0 agents"
    counts = Counter(s.state for s in sessions)
    parts = [f"{total} agents:"]
    for state in ("working", "idle", "needs_input"):
        n = counts.get(state, 0)
        if n:
            parts.append(f"{n} {state}")
    return " ".join([parts[0]] + [", ".join(parts[1:])])


def format_summary_compact(sessions: list[AgentSession]) -> str:
    if not sessions:
        return "0 agents"
    counts = Counter(s.state for s in sessions)
    parts: list[str] = []
    for state in ("working", "idle", "needs_input"):
        n = counts.get(state, 0)
        if n:
            parts.append(f"{COMPACT_ICONS[state]}{n}")
    return " ".join(parts)


def display_results(sessions: list[AgentSession]) -> None:
    console = Console()

    if not sessions:
        console.print("No agent sessions found in tmux.")
        return

    table = Table()
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

    console.print(table)
