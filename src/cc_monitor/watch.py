from __future__ import annotations

import shutil
import subprocess
import time

from loguru import logger
from rich.live import Live
from rich.table import Table

from cc_monitor.analyzer import analyze_sessions
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import STATE_STYLES
from cc_monitor.models import AgentSession


def _notify(title: str, message: str) -> bool:
    tn = shutil.which("terminal-notifier")
    if tn:
        logger.debug("sending notification via terminal-notifier: {}", title)
        subprocess.run(
            [tn, "-title", title, "-message", message, "-sound", "default"],
            capture_output=True,
        )
        return True

    osascript = shutil.which("osascript")
    if osascript:
        logger.debug("falling back to osascript: {}", title)
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run([osascript, "-e", script], capture_output=True)
        return True

    logger.warning("no notification backend available")
    return False


def _detect_transitions(
    prev: list[AgentSession], curr: list[AgentSession]
) -> list[str]:
    prev_needing = {s.tmux_target for s in prev if s.state == "needs_input"}
    transitions: list[str] = []
    for s in curr:
        if s.state == "needs_input" and s.tmux_target not in prev_needing:
            transitions.append(s.tmux_target)
    logger.debug("detected {} needs_input transitions", len(transitions))
    return transitions


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


def watch_loop(interval: float = 2.0, notify: bool = False) -> None:
    logger.info("starting watch mode (interval={:.1f}s, notify={})", interval, notify)
    prev_sessions: list[AgentSession] = []
    with Live(_build_table([]), refresh_per_second=1) as live:
        while True:
            sessions = discover_sessions()
            sessions = analyze_sessions(sessions)
            live.update(_build_table(sessions))
            if notify:
                transitioned = _detect_transitions(prev_sessions, sessions)
                for target in transitioned:
                    _notify("CCM: Input Needed", f"{target} needs input")
            prev_sessions = sessions
            time.sleep(interval)
