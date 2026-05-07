from __future__ import annotations

import sys
from unittest.mock import patch

from cc_monitor.cli import _format_summary, main
from cc_monitor.models import AgentSession


def _make_session(
    state: str = "working",
) -> AgentSession:
    return AgentSession(
        session_name="s",
        window_index=0,
        pane_index=0,
        agent_type="claude",  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="test",
        pane_pid=1,
        tmux_target="s:0.0",
    )


class TestFormatSummary:
    def test_zero_agents(self) -> None:
        assert _format_summary([]) == "0 agents"

    def test_single_working(self) -> None:
        sessions = [_make_session("working")]
        assert _format_summary(sessions) == (
            "1 agents: 1 working"
        )

    def test_mixed_states(self) -> None:
        sessions = [
            _make_session("working"),
            _make_session("working"),
            _make_session("idle"),
        ]
        assert _format_summary(sessions) == (
            "3 agents: 2 working, 1 idle"
        )

    def test_all_states(self) -> None:
        sessions = [
            _make_session("working"),
            _make_session("idle"),
            _make_session("needs_input"),
        ]
        result = _format_summary(sessions)
        assert result == (
            "3 agents: 1 working, 1 idle, 1 needs_input"
        )

    def test_only_idle(self) -> None:
        sessions = [
            _make_session("idle"),
            _make_session("idle"),
        ]
        assert _format_summary(sessions) == (
            "2 agents: 2 idle"
        )

    def test_no_ansi_codes(self) -> None:
        sessions = [_make_session("working")]
        result = _format_summary(sessions)
        assert "\x1b" not in result
        assert "\033" not in result


@patch(
    "cc_monitor.discovery.list_all_panes",
    return_value=[],
)
def test_summary_subcommand(
    mock_panes: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    monkeypatch.setattr(  # type: ignore[attr-defined]
        sys, "argv", ["ccm", "summary"]
    )
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert captured.out == "0 agents"
    assert "\n" not in captured.out
