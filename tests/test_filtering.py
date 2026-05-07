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
        summary="doing stuff",
        pane_pid=1234,
        tmux_target=tmux_target,
    )


SESSIONS = [
    _make_session(agent_type="claude", state="working", tmux_target="a:0.0"),
    _make_session(agent_type="opencode", state="idle", tmux_target="b:1.0"),
    _make_session(agent_type="claude", state="idle", tmux_target="c:2.0"),
    _make_session(agent_type="opencode", state="needs_input", tmux_target="d:3.0"),
]


class TestFilterAndSort:
    def test_no_filters(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="state")
        assert len(result) == 4

    def test_filter_by_state_working(self) -> None:
        result = _filter_and_sort(SESSIONS, state="working", agent=None, sort="state")
        assert len(result) == 1
        assert all(s.state == "working" for s in result)

    def test_filter_by_state_idle(self) -> None:
        result = _filter_and_sort(SESSIONS, state="idle", agent=None, sort="state")
        assert len(result) == 2
        assert all(s.state == "idle" for s in result)

    def test_filter_by_agent_claude(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent="claude", sort="state")
        assert len(result) == 2
        assert all(s.agent_type == "claude" for s in result)

    def test_filter_by_agent_opencode(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent="opencode", sort="state")
        assert len(result) == 2
        assert all(s.agent_type == "opencode" for s in result)

    def test_sort_by_agent_type(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="agent_type")
        types = [s.agent_type for s in result]
        assert types == sorted(types)

    def test_sort_by_tmux_target(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="tmux_target")
        targets = [s.tmux_target for s in result]
        assert targets == sorted(targets)

    def test_sort_by_state(self) -> None:
        result = _filter_and_sort(SESSIONS, state=None, agent=None, sort="state")
        states = [s.state for s in result]
        assert states == sorted(states)

    def test_combined_state_and_agent(self) -> None:
        result = _filter_and_sort(
            SESSIONS, state="idle", agent="claude", sort="state"
        )
        assert len(result) == 1
        assert result[0].agent_type == "claude"
        assert result[0].state == "idle"

    def test_combined_filter_and_sort(self) -> None:
        result = _filter_and_sort(
            SESSIONS, state="idle", agent=None, sort="agent_type"
        )
        assert len(result) == 2
        assert all(s.state == "idle" for s in result)
        types = [s.agent_type for s in result]
        assert types == sorted(types)

    def test_filter_returns_empty(self) -> None:
        result = _filter_and_sort(
            SESSIONS, state="needs_input", agent="claude", sort="state"
        )
        assert len(result) == 0


class TestStatusCLIFlags:
    @patch("cc_monitor.cli.analyze_sessions")
    @patch("cc_monitor.cli.discover_sessions")
    def test_state_flag(
        self,
        mock_discover: object,
        mock_analyze: object,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        mock_discover.return_value = []  # type: ignore[attr-defined]
        mock_analyze.return_value = SESSIONS  # type: ignore[attr-defined]
        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--state", "working", "--json"])  # type: ignore[attr-defined]
        main()
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["state"] == "working"

    @patch("cc_monitor.cli.analyze_sessions")
    @patch("cc_monitor.cli.discover_sessions")
    def test_agent_flag(
        self,
        mock_discover: object,
        mock_analyze: object,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        mock_discover.return_value = []  # type: ignore[attr-defined]
        mock_analyze.return_value = SESSIONS  # type: ignore[attr-defined]
        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--agent", "claude", "--json"])  # type: ignore[attr-defined]
        main()
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert len(data["sessions"]) == 2
        assert all(s["agent_type"] == "claude" for s in data["sessions"])

    @patch("cc_monitor.cli.analyze_sessions")
    @patch("cc_monitor.cli.discover_sessions")
    def test_sort_flag(
        self,
        mock_discover: object,
        mock_analyze: object,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        mock_discover.return_value = []  # type: ignore[attr-defined]
        mock_analyze.return_value = SESSIONS  # type: ignore[attr-defined]
        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--sort", "agent", "--json"])  # type: ignore[attr-defined]
        main()
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        types = [s["agent_type"] for s in data["sessions"]]
        assert types == sorted(types)

    @patch("cc_monitor.cli.analyze_sessions")
    @patch("cc_monitor.cli.discover_sessions")
    def test_combined_flags(
        self,
        mock_discover: object,
        mock_analyze: object,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        mock_discover.return_value = []  # type: ignore[attr-defined]
        mock_analyze.return_value = SESSIONS  # type: ignore[attr-defined]
        monkeypatch.setattr(  # type: ignore[attr-defined]
            sys, "argv", ["ccm", "status", "--state", "idle", "--sort", "agent", "--json"]
        )
        main()
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert len(data["sessions"]) == 2
        assert all(s["state"] == "idle" for s in data["sessions"])
        types = [s["agent_type"] for s in data["sessions"]]
        assert types == sorted(types)
