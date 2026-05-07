from __future__ import annotations

from rich.console import Console
from rich.table import Table

from cc_monitor.models import AgentSession

STATE_STYLES: dict[str, str] = {
    "idle": "green",
    "working": "yellow",
    "needs_input": "bold red",
}


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
