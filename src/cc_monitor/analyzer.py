from __future__ import annotations

import asyncio
import os
import re
import subprocess
import time
from typing import Literal

from loguru import logger

from cc_monitor.llm_provider import LLMProvider, resolve_provider
from cc_monitor.models import AgentSession, AgentState

_SYSTEM_PROMPT = """\
You classify terminal panes from AI coding agents (Claude Code or OpenCode).

State definitions:
- "working": agent is actively processing (spinners, progress bars,
  streaming text, timer counting up like · Xm Xs)
- "idle": agent finished its task. Signs: completion marker
  (Worked/Cooked/Crunched for X), or ▣ marker, followed by empty
  prompt. Agent is done, not asking anything.
- "needs_input": agent asked the user a question or is waiting for
  user to respond/approve something

CRITICAL: An empty prompt after a completion marker = "idle",
NOT "needs_input".

Respond with a JSON object containing exactly two keys:
- "state": one of "working", "idle", or "needs_input"
- "summary": a 5-15 word description of the current task\
"""

_LLM_CONCURRENCY = 4


def capture_pane(tmux_target: str) -> str:
    logger.debug("capturing pane target={}", tmux_target)
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", tmux_target],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


async def _analyze_one_session(
    provider: LLMProvider,
    session: AgentSession,
    tail: str,
    semaphore: asyncio.Semaphore,
) -> bool:
    prompt = (
        f"This is a {session.agent_type} agent terminal pane.\n"
        f"Classify its state and summarize the task in 5-15 words.\n\n{tail}"
    )
    async with semaphore:
        try:
            llm_result = await provider.classify(_SYSTEM_PROMPT, prompt)
            session.state = llm_result.state
            session.summary = llm_result.summary
            logger.debug(
                "{} -> {} {!r}",
                session.tmux_target,
                llm_result.state,
                llm_result.summary,
            )
            return True
        except Exception as e:
            logger.debug("{} LLM classify failed: {}", session.tmux_target, e)
    return False


async def _analyze_with_llm(
    sessions: list[AgentSession],
    pane_contents: dict[str, str],
) -> bool:
    provider_model = os.environ.get("CC_MONITOR_LLM_MODEL", "anthropic-vertex/claude-haiku-4-5@20251001")
    provider = resolve_provider(provider_model)
    semaphore = asyncio.Semaphore(_LLM_CONCURRENCY)

    tasks = []
    for session in sessions:
        content = pane_contents.get(session.tmux_target, "")
        lines = content.splitlines()
        tail = "\n".join(lines[-30:]) if len(lines) > 30 else content
        tasks.append(_analyze_one_session(provider, session, tail, semaphore))
    results = await asyncio.gather(*tasks)

    return any(results)


def analyze_sessions(sessions: list[AgentSession]) -> list[AgentSession]:
    pane_contents: dict[str, str] = {}
    for session in sessions:
        pane_contents[session.tmux_target] = capture_pane(session.tmux_target)

    t0 = time.monotonic()
    try:
        used_llm = asyncio.run(_analyze_with_llm(sessions, pane_contents))
    except Exception as e:
        logger.warning("LLM analysis failed: {}", e)
        used_llm = False
    elapsed_ms = (time.monotonic() - t0) * 1000

    if used_llm:
        logger.debug("LLM analysis completed ({:.0f}ms)", elapsed_ms)
    else:
        logger.debug("LLM unavailable, falling back to regex")
        for session in sessions:
            content = pane_contents.get(session.tmux_target, "")
            lines = content.splitlines()
            session.state = _regex_detect_state(session.agent_type, lines)
            session.summary = _regex_summarize(session.agent_type, lines)

    return sessions


# --- regex fallback (kept for offline/no-API use) ---

_TOOL_CALL_RE = re.compile(r"⏺\s+\w+\(")
_COMPLETION_RE = re.compile(r"✻\s+(Worked|Cooked|Crunched) for")
_OPENCODE_TIMER_RE = re.compile(r"·\s+\d+m\s+\d+s")
_OPENCODE_DONE_RE = re.compile(r"▣\s+Auto-Accept")
_DECORATION_RE = re.compile(r"^[\s─━═▀▁╹┃⏵░█\[\]]*$")


def _regex_detect_state(
    agent_type: Literal["claude", "opencode"], lines: list[str]
) -> AgentState:
    if agent_type == "claude":
        return _regex_detect_claude(lines)
    if agent_type == "opencode":
        return _regex_detect_opencode(lines)
    return "idle"


def _regex_detect_claude(lines: list[str]) -> AgentState:
    if not lines:
        return "idle"
    tail = lines[-10:]
    tail_text = "\n".join(tail)
    bottom = "\n".join(lines[-5:])
    has_prompt = "❯" in bottom
    has_tool_call = bool(_TOOL_CALL_RE.search(tail_text))
    has_completion = bool(_COMPLETION_RE.search(tail_text))
    if has_completion and has_prompt:
        return "idle"
    if has_tool_call and not has_prompt:
        return "working"
    if has_prompt:
        return "needs_input"
    return "working"


def _regex_detect_opencode(lines: list[str]) -> AgentState:
    if not lines:
        return "idle"
    bottom = "\n".join(lines[-5:])
    tail = "\n".join(lines[-10:])
    if _OPENCODE_TIMER_RE.search(bottom):
        return "working"
    if _OPENCODE_DONE_RE.search(tail):
        return "idle"
    return "needs_input"


def _regex_summarize(
    agent_type: Literal["claude", "opencode"], lines: list[str]
) -> str:
    if not lines:
        return ""
    for line in reversed(lines):
        stripped = line.strip()
        if stripped and not _DECORATION_RE.match(stripped):
            return stripped[:80]
    return ""
