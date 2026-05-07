from __future__ import annotations

import os
import re
import subprocess
import time
from typing import Literal

from loguru import logger

from cc_monitor.models import AgentSession

try:
    from anthropic import AnthropicVertex

    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

AgentState = Literal["working", "idle", "needs_input"]


def capture_pane(tmux_target: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", tmux_target],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


_TOOL_CALL_RE = re.compile(r"⏺\s+\w+\(")
_COMPLETION_RE = re.compile(r"✻\s+(Worked|Cooked) for")
_OPENCODE_TIMER_RE = re.compile(r"·\s+\d+m\s+\d+s")
_RECAP_RE = re.compile(r"recap:", re.IGNORECASE)
_TOOL_NAME_RE = re.compile(r"⏺\s+(\w+)\(")
_COMPLETION_DURATION_RE = re.compile(r"✻\s+(?:Worked|Cooked) for\s+(.+)")
_DECORATION_RE = re.compile(r"^[\s─━═▀▁╹┃⏵░█\[\]]*$")


def detect_claude_state(lines: list[str]) -> AgentState:
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

    if has_prompt and not has_tool_call:
        return "needs_input"

    if has_tool_call and has_prompt:
        return "needs_input"

    return "working"


def detect_opencode_state(lines: list[str]) -> AgentState:
    if not lines:
        return "idle"

    bottom = "\n".join(lines[-5:])

    if _OPENCODE_TIMER_RE.search(bottom):
        return "working"

    return "needs_input"


def detect_state(
    agent_type: Literal["claude", "opencode"], lines: list[str]
) -> AgentState:
    if agent_type == "claude":
        return detect_claude_state(lines)
    if agent_type == "opencode":
        return detect_opencode_state(lines)
    return "idle"


def _last_meaningful_line(lines: list[str]) -> str:
    for line in reversed(lines):
        stripped = line.strip()
        if stripped and not _DECORATION_RE.match(stripped):
            return stripped
    return ""


def summarize_claude_activity(lines: list[str]) -> str:
    if not lines:
        return ""

    text = "\n".join(lines)

    for line in lines:
        if _RECAP_RE.search(line):
            idx = line.lower().index("recap:")
            return line[idx + len("recap:") :].strip()

    m = _TOOL_NAME_RE.search(text)
    if m:
        return f"Using {m.group(1)}"

    for line in lines:
        if "thinking" in line.lower():
            return "Thinking..."

    m = _COMPLETION_DURATION_RE.search(text)
    if m:
        return f"Completed {m.group(1).strip()} ago"

    return _last_meaningful_line(lines)


def summarize_opencode_activity(lines: list[str]) -> str:
    if not lines:
        return "Active session"

    bottom = "\n".join(lines[-5:])
    timer_match = _OPENCODE_TIMER_RE.search(bottom)

    content_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _DECORATION_RE.match(stripped):
            continue
        if "Auto-Accept" in stripped or "ctrl+p" in stripped:
            continue
        content_lines.append(stripped)

    if timer_match:
        duration = timer_match.group(0).lstrip("· ").strip()
        if content_lines:
            return f"Processing for {duration} — {content_lines[-1]}"
        return f"Processing for {duration}"

    if content_lines:
        return content_lines[-1]

    return "Active session"


def summarize_activity(
    agent_type: Literal["claude", "opencode"], lines: list[str]
) -> str:
    if agent_type == "claude":
        return summarize_claude_activity(lines)
    if agent_type == "opencode":
        return summarize_opencode_activity(lines)
    return ""


def analyze_pane_llm(text: str) -> str | None:
    if not text.strip():
        logger.debug("analyze_pane_llm: empty pane text, skipping")
        return None

    if not _HAS_ANTHROPIC:
        logger.debug("analyze_pane_llm: anthropic not installed")
        return None

    project_id = os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID")
    if not project_id:
        logger.debug("analyze_pane_llm: missing ANTHROPIC_VERTEX_PROJECT_ID")
        return None

    region = os.environ.get("VERTEX_LOCATION", "global")
    access_token = os.environ.get("VERTEX_ACCESS_TOKEN")
    if not access_token:
        logger.debug("analyze_pane_llm: missing VERTEX_ACCESS_TOKEN")
        return None

    client = AnthropicVertex(
        project_id=project_id,
        region=region,
        access_token=access_token,
    )
    prompt = f"Summarize what this coding agent is doing in one sentence:\n{text}"
    logger.debug("analyze_pane_llm: sending request")
    response = client.messages.create(
        model="claude-sonnet-4-5@20250929",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    block = response.content[0]
    result = block.text if hasattr(block, "text") else None
    logger.debug("analyze_pane_llm: got response: {!r}", result)
    return result


def analyze_sessions(sessions: list[AgentSession]) -> list[AgentSession]:
    for session in sessions:
        t0 = time.monotonic()
        content = capture_pane(session.tmux_target)
        lines = content.splitlines()
        session.state = detect_state(session.agent_type, lines)
        session.summary = summarize_activity(session.agent_type, lines)
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.debug(
            "{} state={} summary={!r} ({:.0f}ms)",
            session.tmux_target,
            session.state,
            session.summary,
            elapsed_ms,
        )
    return sessions
