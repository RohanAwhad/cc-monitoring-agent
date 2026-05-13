from __future__ import annotations

import asyncio
import hashlib
import os
import re
import subprocess
import time
from typing import Literal

from loguru import logger

from cc_monitor.llm_provider import LLMProvider, LLMResult, resolve_provider
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
) -> str | None:
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
            return session.tmux_target
        except Exception as e:
            logger.debug("{} LLM classify failed: {}", session.tmux_target, e)
    return None


async def _analyze_with_llm(
    sessions: list[AgentSession],
    pane_contents: dict[str, str],
) -> set[str]:
    provider_model = os.environ.get(
        "CC_MONITOR_LLM_MODEL", "anthropic-vertex/claude-haiku-4-5@20251001"
    )
    provider = resolve_provider(provider_model)
    semaphore = asyncio.Semaphore(_LLM_CONCURRENCY)

    tasks = []
    for session in sessions:
        content = pane_contents.get(session.tmux_target, "")
        lines = content.splitlines()
        tail = "\n".join(lines[-30:]) if len(lines) > 30 else content
        tasks.append(_analyze_one_session(provider, session, tail, semaphore))
    results = await asyncio.gather(*tasks)

    return {t for t in results if t is not None}


def analyze_sessions(
    sessions: list[AgentSession],
    cache: dict[str, tuple[str, LLMResult]] | None = None,
) -> list[AgentSession]:
    pane_contents: dict[str, str] = {}
    for session in sessions:
        pane_contents[session.tmux_target] = capture_pane(session.tmux_target)

    # Compute tails and content hashes; apply cache hits
    tails: dict[str, str] = {}
    content_hashes: dict[str, str] = {}
    uncached_sessions: list[AgentSession] = []
    for session in sessions:
        content = pane_contents.get(session.tmux_target, "")
        lines = content.splitlines()
        tail = "\n".join(lines[-30:]) if len(lines) > 30 else content
        tails[session.tmux_target] = tail
        content_hash = hashlib.md5(tail.encode()).hexdigest()
        content_hashes[session.tmux_target] = content_hash

        if cache is not None:
            cached = cache.get(session.tmux_target)
            if cached is not None:
                stored_hash, stored_result = cached
                if stored_hash == content_hash:
                    session.state = stored_result.state
                    session.summary = stored_result.summary
                    logger.debug("{} cache hit, skipping LLM", session.tmux_target)
                    continue
        uncached_sessions.append(session)

    # Run LLM only for uncached sessions
    t0 = time.monotonic()
    succeeded_targets: set[str] = set()
    if uncached_sessions:
        uncached_contents = {
            s.tmux_target: pane_contents.get(s.tmux_target, "")
            for s in uncached_sessions
        }
        try:
            succeeded_targets = asyncio.run(
                _analyze_with_llm(uncached_sessions, uncached_contents)
            )
        except Exception as e:
            logger.warning("LLM analysis failed: {}", e)
    elapsed_ms = (time.monotonic() - t0) * 1000

    if succeeded_targets:
        logger.debug("LLM analysis completed ({:.0f}ms)", elapsed_ms)
        # Store LLM results in cache (only for sessions that succeeded)
        if cache is not None:
            for session in uncached_sessions:
                if session.tmux_target not in succeeded_targets:
                    continue
                content = pane_contents.get(session.tmux_target, "")
                if not content:
                    continue  # don't cache empty captures
                content_hash = content_hashes[session.tmux_target]
                cache[session.tmux_target] = (
                    content_hash,
                    LLMResult(state=session.state, summary=session.summary),
                )

    # Regex fallback for uncached sessions where LLM did not succeed
    for session in uncached_sessions:
        if session.tmux_target in succeeded_targets:
            continue
        logger.debug("LLM unavailable for {}, regex fallback", session.tmux_target)
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
