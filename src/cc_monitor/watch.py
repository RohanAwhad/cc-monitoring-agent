from __future__ import annotations

import shutil
import subprocess
import time
from collections.abc import Mapping

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


def _detect_transitions(
    previous: Mapping[str, str], current: Mapping[str, str]
) -> list[str]:
    transitioned: list[str] = []
    for target, state in current.items():
        if state == "needs_input" and previous.get(target) != "needs_input":
            transitioned.append(target)
    return transitioned


def _send_desktop_alert(title: str, message: str) -> None:
    if shutil.which("terminal-notifier"):
        subprocess.run(
            ["terminal-notifier", "-title", title, "-message", message],
            capture_output=True,
        )
    else:
        logger.warning(
            "terminal-notifier not found, falling back to osascript "
            "(may not work on macOS Sequoia)"
        )
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
        )


def watch_loop(interval: float = 2.0, notify: bool = False) -> None:
    logger.info("starting watch mode (interval={:.1f}s, notify={})", interval, notify)
    previous_states: Mapping[str, str] = {}
    with Live(_build_table([]), refresh_per_second=1) as live:
        while True:
            sessions = discover_sessions()
            sessions = analyze_sessions(sessions)
            live.update(_build_table(sessions))

            if notify:
                current_states = {s.tmux_target: s.state for s in sessions}
                transitioned = _detect_transitions(previous_states, current_states)
                for target in transitioned:
                    logger.info("session {} needs input, sending alert", target)
                    _send_desktop_alert(
                        "CCM: Input Required",
                        f"Session {target} needs your input",
                    )
                previous_states = current_states

            time.sleep(interval)
