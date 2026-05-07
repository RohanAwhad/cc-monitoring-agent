from __future__ import annotations

import json
import sys
from unittest.mock import patch

from cc_monitor.cli import _apply_session_filters, _apply_session_ordering, main
from cc_monitor.models import AgentSession


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_main_runs(mock_panes: object, monkeypatch: object) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_json_output(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_help(mock_panes: object, monkeypatch: object, capsys: object) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "--help"])  # type: ignore[attr-defined]
    try:
        main()
    except SystemExit:
        pass
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "usage" in captured.out.lower() or "ccm" in captured.out


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_subcommand(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_bare_ccm_defaults_to_status(
    mock_panes: object, monkeypatch: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_bare_ccm_json_backward_compat(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


def _make_session(
    agent_type: str = "claude",
    state: str = "working",
    tmux_target: str = "test:0.0",
) -> AgentSession:
    return AgentSession(
        session_name="test",
        window_index=0,
        pane_index=0,
        agent_type=agent_type,  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="test summary",
        pane_pid=1234,
        tmux_target=tmux_target,
    )


class TestApplySessionFilters:
    def test_no_filters(self) -> None:
        sessions = [_make_session(), _make_session(agent_type="opencode")]
        result = _apply_session_filters(sessions, state=None, agent=None)
        assert len(result) == 2

    def test_filter_by_state(self) -> None:
        sessions = [
            _make_session(state="working"),
            _make_session(state="idle"),
            _make_session(state="needs_input"),
        ]
        result = _apply_session_filters(sessions, state="idle", agent=None)
        assert len(result) == 1
        assert result[0].state == "idle"

    def test_filter_by_agent(self) -> None:
        sessions = [
            _make_session(agent_type="claude"),
            _make_session(agent_type="opencode"),
            _make_session(agent_type="claude"),
        ]
        result = _apply_session_filters(sessions, state=None, agent="opencode")
        assert len(result) == 1
        assert result[0].agent_type == "opencode"

    def test_filter_by_both(self) -> None:
        sessions = [
            _make_session(agent_type="claude", state="working"),
            _make_session(agent_type="claude", state="idle"),
            _make_session(agent_type="opencode", state="working"),
        ]
        result = _apply_session_filters(sessions, state="working", agent="claude")
        assert len(result) == 1
        assert result[0].agent_type == "claude"
        assert result[0].state == "working"

    def test_filter_returns_empty(self) -> None:
        sessions = [_make_session(state="working")]
        result = _apply_session_filters(sessions, state="idle", agent=None)
        assert result == []


class TestApplySessionOrdering:
    def test_sort_by_state(self) -> None:
        sessions = [
            _make_session(state="working"),
            _make_session(state="idle"),
            _make_session(state="needs_input"),
        ]
        result = _apply_session_ordering(sessions, key="state")
        assert [s.state for s in result] == ["idle", "needs_input", "working"]

    def test_sort_by_agent_type(self) -> None:
        sessions = [
            _make_session(agent_type="opencode"),
            _make_session(agent_type="claude"),
        ]
        result = _apply_session_ordering(sessions, key="agent_type")
        assert [s.agent_type for s in result] == ["claude", "opencode"]

    def test_sort_by_tmux_target(self) -> None:
        sessions = [
            _make_session(tmux_target="z:0.0"),
            _make_session(tmux_target="a:0.0"),
        ]
        result = _apply_session_ordering(sessions, key="tmux_target")
        assert [s.tmux_target for s in result] == ["a:0.0", "z:0.0"]
