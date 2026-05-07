from __future__ import annotations

from loguru import logger

from cc_monitor.models import AgentSession


def filter_sessions(
    sessions: list[AgentSession],
    state: str | None,
    agent: str | None,
) -> list[AgentSession]:
    logger.debug(
        "filter_sessions: state={!r} agent={!r} count={}",
        state,
        agent,
        len(sessions),
    )
    result = sessions
    if state is not None:
        result = [s for s in result if s.state == state]
    if agent is not None:
        result = [s for s in result if s.agent_type == agent]
    logger.debug("filter_sessions returning {} sessions", len(result))
    return result


def sort_sessions(
    sessions: list[AgentSession],
    sort_key: str,
) -> list[AgentSession]:
    logger.debug("sort_sessions called: key={!r} count={}", sort_key, len(sessions))
    return sorted(sessions, key=lambda s: getattr(s, sort_key))
