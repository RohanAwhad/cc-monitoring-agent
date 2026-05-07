from __future__ import annotations

from typing import Any

from loguru import logger
from rich.console import Console
from rich.table import Table

from cc_monitor.models import AgentSession

STATE_STYLES: dict[str, str] = {
    "idle": "green",
    "working": "yellow",
    "needs_input": "bold red",
}


def _format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def display_results(
    sessions: list[AgentSession],
    cost_data: dict[str, dict[str, Any] | None] | None = None,
) -> None:
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

    show_costs = cost_data is not None
    if show_costs:
        table.add_column("Tokens In", justify="right")
        table.add_column("Tokens Out", justify="right")
        table.add_column("Cost ($)", justify="right")

    for s in sessions:
        style = STATE_STYLES.get(s.state, "")
        logger.debug("rendering row: target={} state={}", s.tmux_target, s.state)
        row: list[str] = [
            s.tmux_target,
            s.agent_type,
            f"[{style}]{s.state}[/{style}]" if style else s.state,
            s.summary,
        ]
        if show_costs:
            assert cost_data is not None
            cd = cost_data.get(s.tmux_target)
            if cd is not None:
                inp = cd.get("input_tokens", 0)
                out = cd.get("output_tokens", 0)
                cost = cd.get("estimated_cost_usd", 0)
                row.append(_format_tokens(int(inp or 0)))
                row.append(_format_tokens(int(out or 0)))
                row.append(f"{cost:.4f}")
            else:
                row.extend(["-", "-", "-"])
        table.add_row(*row)

    console.print(table)
