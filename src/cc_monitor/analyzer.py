from __future__ import annotations

import re
import subprocess


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


def detect_claude_state(lines: list[str]) -> str:
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


def detect_opencode_state(lines: list[str]) -> str:
    if not lines:
        return "idle"

    bottom = "\n".join(lines[-5:])

    if _OPENCODE_TIMER_RE.search(bottom):
        return "working"

    return "needs_input"


def detect_state(agent_type: str, lines: list[str]) -> str:
    if agent_type == "claude":
        return detect_claude_state(lines)
    if agent_type == "opencode":
        return detect_opencode_state(lines)
    return "idle"
