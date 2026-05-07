from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

from cc_monitor.cli import main
from cc_monitor.filtering import filter_sessions, sort_sessions
from cc_monitor.models import AgentSession


def _make_session(
    agent_type: str = "claude",
    state: str = "working",
    tmux_target: str = "dev:0.0",
) -> AgentSession:
    parts = tmux_target.split(":")
    session_name = parts[0]
    win_pane = parts[1].split(".")
    return AgentSession(
        session_name=session_name,
        window_index=int(win_pane[0]),
        pane_index=int(win_pane[1]),
        agent_type=agent_type,  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary="test",
        pane_pid=100,
        tmux_target=tmux_target,
    )


class TestFilterSessions:
    def test_no_filters(self) -> None:
        sessions = [_make_session(), _make_session(state="idle")]
        result = filter_sessions(sessions, state=None, agent=None)
        assert len(result) == 2

    def test_filter_by_state(self) -> None:
        sessions = [
            _make_session(state="working"),
            _make_session(state="idle"),
            _make_session(state="needs_input"),
        ]
        result = filter_sessions(sessions, state="working", agent=None)
        assert len(result) == 1
        assert result[0].state == "working"

    def test_filter_by_agent(self) -> None:
        sessions = [
            _make_session(agent_type="claude"),
            _make_session(agent_type="opencode"),
        ]
        result = filter_sessions(sessions, state=None, agent="claude")
        assert len(result) == 1
        assert result[0].agent_type == "claude"

    def test_filter_by_state_and_agent(self) -> None:
        sessions = [
            _make_session(agent_type="claude", state="working"),
            _make_session(agent_type="claude", state="idle"),
            _make_session(agent_type="opencode", state="working"),
        ]
        result = filter_sessions(sessions, state="working", agent="claude")
        assert len(result) == 1
        assert result[0].agent_type == "claude"
        assert result[0].state == "working"

    def test_filter_returns_empty(self) -> None:
        sessions = [_make_session(state="working")]
        result = filter_sessions(sessions, state="idle", agent=None)
        assert result == []

    def test_filter_empty_input(self) -> None:
        result = filter_sessions([], state="working", agent=None)
        assert result == []


class TestSortSessions:
    def test_sort_by_state(self) -> None:
        sessions = [
            _make_session(state="working"),
            _make_session(state="idle"),
            _make_session(state="needs_input"),
        ]
        result = sort_sessions(sessions, "state")
        assert [s.state for s in result] == ["idle", "needs_input", "working"]

    def test_sort_by_agent_type(self) -> None:
        sessions = [
            _make_session(agent_type="opencode"),
            _make_session(agent_type="claude"),
        ]
        result = sort_sessions(sessions, "agent_type")
        assert [s.agent_type for s in result] == ["claude", "opencode"]

    def test_sort_by_tmux_target(self) -> None:
        sessions = [
            _make_session(tmux_target="zz:1.0"),
            _make_session(tmux_target="aa:0.0"),
        ]
        result = sort_sessions(sessions, "tmux_target")
        assert [s.tmux_target for s in result] == ["aa:0.0", "zz:1.0"]

    def test_sort_empty(self) -> None:
        result = sort_sessions([], "state")
        assert result == []


TMUX_OUTPUT = "writer-cc:1.0 2.1.119 57697\nagents-py:2.1 opencode 95294\n"

PS_OUTPUT = """\
  PID  PPID COMM
57698 57697 claude
95295 95294 opencode
"""

CLAUDE_CONTENT = "⏺ Read(src/file.py)\n"
OPENCODE_CONTENT = "some output\n"


def _subprocess_side_effect(
    tmux_out: str, ps_out: str, pane_contents: dict[str, str]
) -> object:
    def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
        if cmd[0] == "tmux" and "list-panes" in cmd:
            return MagicMock(returncode=0, stdout=tmux_out)
        if cmd[0] == "ps":
            return MagicMock(returncode=0, stdout=ps_out)
        if cmd[0] == "tmux" and "capture-pane" in cmd:
            target = cmd[cmd.index("-t") + 1]
            content = pane_contents.get(target, "")
            return MagicMock(returncode=0, stdout=content)
        return MagicMock(returncode=1, stdout="")

    return side_effect


class TestCLIFilteringFlags:
    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_state_flag_filters_json(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {
            "writer-cc:1.0": CLAUDE_CONTENT,
            "agents-py:2.1": OPENCODE_CONTENT,
        }
        effect = _subprocess_side_effect(TMUX_OUTPUT, PS_OUTPUT, pane_contents)
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json", "--agent", "claude"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        for s in data["sessions"]:
            assert s["agent_type"] == "claude"

    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_sort_flag_json(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {
            "writer-cc:1.0": CLAUDE_CONTENT,
            "agents-py:2.1": OPENCODE_CONTENT,
        }
        effect = _subprocess_side_effect(TMUX_OUTPUT, PS_OUTPUT, pane_contents)
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json", "--sort", "tmux_target"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        targets = [s["tmux_target"] for s in data["sessions"]]
        assert targets == sorted(targets)

    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_combined_flags(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {
            "writer-cc:1.0": CLAUDE_CONTENT,
            "agents-py:2.1": OPENCODE_CONTENT,
        }
        effect = _subprocess_side_effect(TMUX_OUTPUT, PS_OUTPUT, pane_contents)
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(  # type: ignore[attr-defined]
            sys, "argv", ["ccm", "status", "--json", "--agent", "opencode", "--sort", "tmux_target"]
        )
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        for s in data["sessions"]:
            assert s["agent_type"] == "opencode"

    @patch("cc_monitor.discovery.list_all_panes", return_value=[])
    def test_state_flag_with_no_sessions(
        self,
        mock_panes: object,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json", "--state", "working"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert data == {"sessions": []}
