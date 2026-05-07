from __future__ import annotations

import json
import sys
from unittest.mock import patch

from cc_monitor.cli import _filter_and_sort, main
from cc_monitor.models import AgentSession


def _make_session(
    agent_type: str = "claude",
    state: str = "working",
    tmux_target: str = "main:0.0",
) -> AgentSession:
    return AgentSession(
        session_name="main",
        window_index=0,
        pane_index=0,
        agent_type=agent_type,  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="test",
        pane_pid=1234,
        tmux_target=tmux_target,
    )


SESSIONS = [
    _make_session(agent_type="claude", state="working", tmux_target="a:0.0"),
    _make_session(agent_type="opencode", state="idle", tmux_target="b:0.0"),
    _make_session(agent_type="claude", state="idle", tmux_target="c:0.0"),
    _make_session(agent_type="opencode", state="needs_input", tmux_target="d:0.0"),
]


def test_filter_by_state_working() -> None:
    result = _filter_and_sort(SESSIONS, state="working", agent=None, sort="state")
    assert len(result) == 1
    assert result[0].state == "working"


def test_filter_by_state_idle() -> None:
    result = _filter_and_sort(SESSIONS, state="idle", agent=None, sort="state")
    assert len(result) == 2
    assert all(s.state == "idle" for s in result)


def test_filter_by_agent_claude() -> None:
    result = _filter_and_sort(SESSIONS, state=None, agent="claude", sort="state")
    assert len(result) == 2
    assert all(s.agent_type == "claude" for s in result)


def test_filter_by_agent_opencode() -> None:
    result = _filter_and_sort(SESSIONS, state=None, agent="opencode", sort="state")
    assert len(result) == 2
    assert all(s.agent_type == "opencode" for s in result)


def test_sort_by_agent_type() -> None:
    result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="agent_type")
    agent_types = [s.agent_type for s in result]
    assert agent_types == sorted(agent_types)


def test_sort_by_tmux_target() -> None:
    result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="tmux_target")
    targets = [s.tmux_target for s in result]
    assert targets == sorted(targets)


def test_combined_state_and_sort() -> None:
    result = _filter_and_sort(SESSIONS, state="idle", agent=None, sort="agent_type")
    assert len(result) == 2
    assert all(s.state == "idle" for s in result)
    agent_types = [s.agent_type for s in result]
    assert agent_types == sorted(agent_types)


def test_combined_state_and_agent() -> None:
    result = _filter_and_sort(SESSIONS, state="idle", agent="claude", sort="state")
    assert len(result) == 1
    assert result[0].agent_type == "claude"
    assert result[0].state == "idle"


def test_no_filters_returns_all_sorted() -> None:
    result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="state")
    assert len(result) == len(SESSIONS)


def test_filter_no_matches() -> None:
    result = _filter_and_sort(SESSIONS, state="needs_input", agent="claude", sort="state")
    assert len(result) == 0


@patch("cc_monitor.cli.discover_sessions", return_value=[])
@patch("cc_monitor.cli.analyze_sessions", return_value=[])
def test_cli_status_state_flag(
    mock_analyze: object, mock_discover: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--state", "working", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.cli.discover_sessions", return_value=[])
@patch("cc_monitor.cli.analyze_sessions", return_value=[])
def test_cli_status_agent_flag(
    mock_analyze: object, mock_discover: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--agent", "claude", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.cli.discover_sessions", return_value=[])
@patch("cc_monitor.cli.analyze_sessions", return_value=[])
def test_cli_status_sort_flag(
    mock_analyze: object, mock_discover: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--sort", "agent_type", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data
