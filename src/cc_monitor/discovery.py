from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Literal

from loguru import logger

from cc_monitor.models import AgentSession

_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass
class RawPane:
    session_name: str
    window_index: int
    pane_index: int
    current_command: str
    pane_pid: int


def list_all_panes() -> list[RawPane]:
    result = subprocess.run(
        [
            "tmux",
            "list-panes",
            "-a",
            "-F",
            "#{session_name}:#{window_index}.#{pane_index}"
            " #{pane_current_command} #{pane_pid}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.debug("tmux list-panes failed (rc={})", result.returncode)
        return []
    panes = _parse_pane_lines(result.stdout)
    logger.debug("found {} tmux panes", len(panes))
    return panes


def _parse_pane_lines(output: str) -> list[RawPane]:
    panes: list[RawPane] = []
    for line in output.strip().splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        target = parts[0]
        command = parts[1]
        pid_str = parts[2]
        match = re.match(r"^(.+):(\d+)\.(\d+)$", target)
        if not match:
            continue
        panes.append(
            RawPane(
                session_name=match.group(1),
                window_index=int(match.group(2)),
                pane_index=int(match.group(3)),
                current_command=command,
                pane_pid=int(pid_str),
            )
        )
    return panes


PaneClass = Literal[
    "claude_candidate",
    "opencode",
    "gemini",
    "codex",
    "other",
]


def classify_pane(pane: RawPane) -> PaneClass:
    cmd = pane.current_command
    if cmd == "opencode":
        return "opencode"
    if cmd == "gemini":
        return "gemini"
    if cmd == "codex":
        return "codex"
    if _VERSION_RE.match(cmd):
        return "claude_candidate"
    return "other"


def verify_claude_candidate(pane_pid: int) -> bool:
    result = subprocess.run(
        ["ps", "-eo", "pid,ppid,comm"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    return _check_child_processes(result.stdout, pane_pid)


def _check_child_processes(ps_output: str, parent_pid: int) -> bool:
    for line in ps_output.strip().splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        ppid_str = parts[1]
        comm = parts[2]
        if int(ppid_str) == parent_pid and "claude" in comm.lower():
            return True
    return False


def discover_sessions() -> list[AgentSession]:
    panes = list_all_panes()
    sessions: list[AgentSession] = []
    for pane in panes:
        classification = classify_pane(pane)
        logger.debug(
            "pane {}:{}.{} cmd={!r} -> {}",
            pane.session_name,
            pane.window_index,
            pane.pane_index,
            pane.current_command,
            classification,
        )
        if classification in ("opencode", "gemini", "codex"):
            agent_type: Literal["opencode", "gemini", "codex"] = classification
            sessions.append(
                AgentSession(
                    session_name=pane.session_name,
                    window_index=pane.window_index,
                    pane_index=pane.pane_index,
                    agent_type=agent_type,
                    state="idle",
                    summary="",
                    pane_pid=pane.pane_pid,
                    tmux_target=(
                        f"{pane.session_name}:{pane.window_index}.{pane.pane_index}"
                    ),
                )
            )
        elif classification == "claude_candidate":
            verified = verify_claude_candidate(pane.pane_pid)
            logger.debug("claude candidate pid={} verified={}", pane.pane_pid, verified)
            if verified:
                sessions.append(
                    AgentSession(
                        session_name=pane.session_name,
                        window_index=pane.window_index,
                        pane_index=pane.pane_index,
                        agent_type="claude",
                        state="idle",
                        summary="",
                        pane_pid=pane.pane_pid,
                        tmux_target=f"{pane.session_name}:{pane.window_index}.{pane.pane_index}",
                    )
                )
    return sessions
