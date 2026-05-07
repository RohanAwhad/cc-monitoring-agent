from __future__ import annotations

from cc_monitor.display import format_summary, format_summary_compact
from cc_monitor.models import AgentSession


def _make_session(
    state: str = "working",
    tmux_target: str = "main:0.0",
) -> AgentSession:
    parts = tmux_target.split(":")
    session_name = parts[0]
    wp = parts[1].split(".")
    return AgentSession(
        session_name=session_name,
        window_index=int(wp[0]),
        pane_index=int(wp[1]),
        agent_type="claude",  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="test",
        pane_pid=1234,
        tmux_target=tmux_target,
    )


class TestFormatSummary:
    def test_zero_sessions(self) -> None:
        assert format_summary([]) == "0 agents"

    def test_single_working(self) -> None:
        result = format_summary([_make_session("working")])
        assert result == "3 agents:" or "1 agents:" in result or result == "1 agents: 1 working"
        assert "1 working" in result

    def test_mixed_states(self) -> None:
        sessions = [
            _make_session("working"),
            _make_session("working"),
            _make_session("idle"),
            _make_session("needs_input"),
        ]
        result = format_summary(sessions)
        assert result.startswith("4 agents:")
        assert "2 working" in result
        assert "1 idle" in result
        assert "1 needs_input" in result

    def test_no_trailing_newline(self) -> None:
        result = format_summary([_make_session("idle")])
        assert not result.endswith("\n")


class TestFormatSummaryCompact:
    def test_zero_sessions(self) -> None:
        assert format_summary_compact([]) == "0 agents"

    def test_single_working(self) -> None:
        result = format_summary_compact([_make_session("working")])
        assert "⚡1" in result

    def test_mixed_states(self) -> None:
        sessions = [
            _make_session("working"),
            _make_session("working"),
            _make_session("idle"),
            _make_session("needs_input"),
        ]
        result = format_summary_compact(sessions)
        assert "⚡2" in result
        assert "🕐1" in result
        assert "❗1" in result

    def test_no_trailing_newline(self) -> None:
        result = format_summary_compact([_make_session("idle")])
        assert not result.endswith("\n")

    def test_omits_zero_count_states(self) -> None:
        sessions = [_make_session("working")]
        result = format_summary_compact(sessions)
        assert "🕐" not in result
        assert "❗" not in result
