from __future__ import annotations

import json
import sys
from unittest.mock import patch

from cc_monitor.cli import filter_sessions, sort_sessions, main
from cc_monitor.models import AgentSession


def _make_session(
    *,
    name: str = "s",
    agent_type: str = "claude",
    state: str = "working",
) -> AgentSession:
    return AgentSession(
        session_name=name,
        window_index=0,
        pane_index=0,
        agent_type=agent_type,  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="",
        pane_pid=1,
        tmux_target=f"{name}:0.0",
    )


SESSIONS = [
    _make_session(name="a", agent_type="claude", state="working"),
    _make_session(name="b", agent_type="opencode", state="idle"),
    _make_session(name="c", agent_type="claude", state="needs_input"),
    _make_session(name="d", agent_type="opencode", state="working"),
]


def test_filter_by_state_working() -> None:
    result = filter_sessions(SESSIONS, state="working")
    assert len(result) == 2
    assert all(s.state == "working" for s in result)


def test_filter_by_state_idle() -> None:
    result = filter_sessions(SESSIONS, state="idle")
    assert len(result) == 1
    assert result[0].session_name == "b"


def test_filter_by_state_needs_input() -> None:
    result = filter_sessions(SESSIONS, state="needs_input")
    assert len(result) == 1
    assert result[0].session_name == "c"


def test_filter_by_agent_claude() -> None:
    result = filter_sessions(SESSIONS, agent="claude")
    assert len(result) == 2
    assert all(s.agent_type == "claude" for s in result)


def test_filter_by_agent_opencode() -> None:
    result = filter_sessions(SESSIONS, agent="opencode")
    assert len(result) == 2
    assert all(s.agent_type == "opencode" for s in result)


def test_filter_combined() -> None:
    result = filter_sessions(SESSIONS, state="working", agent="claude")
    assert len(result) == 1
    assert result[0].session_name == "a"


def test_filter_empty_result() -> None:
    result = filter_sessions(SESSIONS, state="idle", agent="claude")
    assert result == []


def test_filter_no_filters() -> None:
    result = filter_sessions(SESSIONS)
    assert len(result) == 4


def test_sort_by_state() -> None:
    result = sort_sessions(SESSIONS, key="state")
    states = [s.state for s in result]
    assert states == sorted(states)


def test_sort_by_agent() -> None:
    result = sort_sessions(SESSIONS, key="agent")
    agents = [s.agent_type for s in result]
    assert agents == sorted(agents)


def test_sort_by_session() -> None:
    shuffled = [SESSIONS[2], SESSIONS[0], SESSIONS[3], SESSIONS[1]]
    result = sort_sessions(shuffled, key="session")
    names = [s.session_name for s in result]
    assert names == ["a", "b", "c", "d"]


def test_sort_none_preserves_order() -> None:
    result = sort_sessions(SESSIONS, key=None)
    assert result is SESSIONS


def test_sort_unknown_key_preserves_order() -> None:
    result = sort_sessions(SESSIONS, key="unknown")
    assert result is SESSIONS


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_with_state_flag(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--state", "working", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_with_agent_flag(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--agent", "claude", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_with_sort_flag(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--sort", "state", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_combined_flags(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(  # type: ignore[attr-defined]
        sys,
        "argv",
        ["ccm", "status", "--state", "working", "--agent", "claude", "--sort", "state", "--json"],
    )
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data
