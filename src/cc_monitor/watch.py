from __future__ import annotations

import subprocess
import time

from loguru import logger
from rich.live import Live
from rich.table import Table

from cc_monitor.analyzer import analyze_sessions
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import STATE_STYLES
from cc_monitor.models import AgentSession


def _build_table(sessions: list[AgentSession]) -> Table:
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


def detect_state_changes(
    previous: dict[str, str], current: dict[str, str]
) -> list[tuple[str, str, str]]:
    changes: list[tuple[str, str, str]] = []
    for target, new_state in current.items():
        old_state = previous.get(target)
        if old_state is not None and old_state != new_state:
            changes.append((target, old_state, new_state))
    return changes


def send_notification(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}"'
    logger.debug("sending notification: {} - {}", title, message)
    subprocess.run(["osascript", "-e", script], check=False)


def _build_state_map(sessions: list[AgentSession]) -> dict[str, str]:
    return {s.tmux_target: s.state for s in sessions}


def watch_loop(interval: float = 2.0, notify: bool = False) -> None:
    logger.info("starting watch mode (interval={:.1f}s, notify={})", interval, notify)
    previous_states: dict[str, str] | None = None
    with Live(_build_table([]), refresh_per_second=1) as live:
        while True:
            sessions = discover_sessions()
            sessions = analyze_sessions(sessions)
            live.update(_build_table(sessions))

            if notify:
                current_states = _build_state_map(sessions)
                if previous_states is not None:
                    changes = detect_state_changes(previous_states, current_states)
                    for target, old_state, new_state in changes:
                        if new_state == "needs_input":
                            send_notification(
                                "CCM: Input Needed",
                                f"{target} changed from {old_state} to {new_state}",
                            )
                previous_states = current_states

            time.sleep(interval)
