from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Literal

from loguru import logger

from cc_monitor.models import AgentSession

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


def _capture_pane_cwd(tmux_target: str) -> str:
    result = subprocess.run(
        ["tmux", "display-message", "-t", tmux_target, "-p", "#{pane_current_path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def analyze_sessions(sessions: list[AgentSession]) -> list[AgentSession]:
    for session in sessions:
        t0 = time.monotonic()
        content = capture_pane(session.tmux_target)
        lines = content.splitlines()
        session.state = detect_state(session.agent_type, lines)
        session.summary = summarize_activity(session.agent_type, lines)
        session.cwd = _capture_pane_cwd(session.tmux_target)
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.debug(
            "{} state={} summary={!r} cwd={!r} ({:.0f}ms)",
            session.tmux_target,
            session.state,
            session.summary,
            session.cwd,
            elapsed_ms,
        )
    return sessions


COST_PER_MTOK: dict[str, tuple[float, float]] = {
    "sonnet": (3.0, 15.0),
    "opus": (15.0, 75.0),
    "haiku": (0.80, 4.0),
}


def _model_to_tier(model: str) -> str:
    model_lower = model.lower()
    for tier in COST_PER_MTOK:
        if tier in model_lower:
            return tier
    return "sonnet"


def _cwd_to_project_dir_name(cwd: str) -> str:
    return cwd.replace("/", "-")


def _find_conversation_files(cwd: str, claude_dir: Path | None = None) -> list[Path]:
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"
    projects_dir = claude_dir / "projects"
    if not projects_dir.is_dir():
        return []
    dir_name = _cwd_to_project_dir_name(cwd)
    project_dir = projects_dir / dir_name
    if not project_dir.is_dir():
        return []
    return sorted(project_dir.glob("*.jsonl"))


def _parse_usage_from_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text().splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        entry: dict[str, Any] = json.loads(raw_line)
        msg: dict[str, Any] = entry.get("message", {})
        usage: dict[str, Any] | None = msg.get("usage")
        if usage is None:
            continue
        model: str = msg.get("model", "")
        records.append({"model": model, "usage": usage})
    return records


def estimate_session_cost(
    session: AgentSession, claude_dir: Path | None = None
) -> dict[str, object] | None:
    if not session.cwd:
        return None
    cwd = session.cwd

    conv_files = _find_conversation_files(cwd, claude_dir)
    if not conv_files:
        return None

    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    total_cost = 0.0

    for conv_file in conv_files:
        records = _parse_usage_from_jsonl(conv_file)
        for rec in records:
            usage = rec["usage"]
            inp = usage.get("input_tokens", 0)
            out = usage.get("output_tokens", 0)
            cache_create = usage.get("cache_creation_input_tokens", 0)
            cache_read = usage.get("cache_read_input_tokens", 0)

            total_input += inp
            total_output += out
            total_cache_creation += cache_create
            total_cache_read += cache_read

            tier = _model_to_tier(rec.get("model", ""))
            input_price, output_price = COST_PER_MTOK[tier]
            cost = (inp * input_price + out * output_price) / 1_000_000
            cache_write_price = input_price * 1.25
            cache_read_price = input_price * 0.1
            cost += (
                cache_create * cache_write_price + cache_read * cache_read_price
            ) / 1_000_000
            total_cost += cost

    all_zero = (
        total_input == 0
        and total_output == 0
        and total_cache_creation == 0
        and total_cache_read == 0
    )
    if all_zero:
        return None

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_creation_tokens": total_cache_creation,
        "cache_read_tokens": total_cache_read,
        "estimated_cost_usd": round(total_cost, 4),
    }
