from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from loguru import logger

AgentState = Literal["working", "idle", "needs_input"]


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

    def __post_init__(self) -> None:
        logger.debug(
            "AgentSession created: target={} agent={} state={}",
            self.tmux_target,
            self.agent_type,
            self.state,
        )
