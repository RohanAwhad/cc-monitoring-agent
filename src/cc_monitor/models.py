from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class AgentSession:
    session_name: str
    window_index: int
    pane_index: int
    agent_type: Literal["claude", "opencode"]
    state: Literal["working", "idle", "needs_input"]
    summary: str
    pane_pid: int
    tmux_target: str
