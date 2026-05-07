from __future__ import annotations

from unittest.mock import MagicMock, patch

from cc_monitor.discovery import (
    RawPane,
    _check_child_processes,
    _parse_pane_lines,
    classify_pane,
    discover_sessions,
    list_all_panes,
    verify_claude_candidate,
)

TMUX_OUTPUT = """\
writer-cc:1.0 2.1.119 57697
cleanup:2.1 2.1.118 22347
agents-py:2.1 opencode 95294
factory:1.1 opencode 40301
dev:0.0 zsh 12345
build:1.0 vim 99999
"""

PS_OUTPUT = """\
  PID  PPID COMM
57698 57697 claude
22348 22347 claude
95295 95294 opencode
40302 40301 opencode
12346 12345 zsh
"""


class TestParsePaneLines:
    def test_parses_valid_lines(self) -> None:
        panes = _parse_pane_lines(TMUX_OUTPUT)
        assert len(panes) == 6
        assert panes[0].session_name == "writer-cc"
        assert panes[0].window_index == 1
        assert panes[0].pane_index == 0
        assert panes[0].current_command == "2.1.119"
        assert panes[0].pane_pid == 57697

    def test_opencode_pane(self) -> None:
        panes = _parse_pane_lines(TMUX_OUTPUT)
        oc = panes[2]
        assert oc.session_name == "agents-py"
        assert oc.current_command == "opencode"
        assert oc.pane_pid == 95294

    def test_empty_output(self) -> None:
        assert _parse_pane_lines("") == []
        assert _parse_pane_lines("   \n  \n") == []

    def test_malformed_line_skipped(self) -> None:
        panes = _parse_pane_lines("not-a-target cmd\n")
        assert panes == []


class TestClassifyPane:
    def test_opencode(self) -> None:
        pane = RawPane("s", 0, 0, "opencode", 100)
        assert classify_pane(pane) == "opencode"

    def test_claude_candidate(self) -> None:
        pane = RawPane("s", 0, 0, "2.1.119", 100)
        assert classify_pane(pane) == "claude_candidate"

    def test_other_version_pattern(self) -> None:
        pane = RawPane("s", 0, 0, "10.20.300", 100)
        assert classify_pane(pane) == "claude_candidate"

    def test_other_command(self) -> None:
        for cmd in ["zsh", "vim", "python3", "bash", "node"]:
            pane = RawPane("s", 0, 0, cmd, 100)
            assert classify_pane(pane) == "other"

    def test_partial_version_not_matched(self) -> None:
        pane = RawPane("s", 0, 0, "2.1", 100)
        assert classify_pane(pane) == "other"


class TestCheckChildProcesses:
    def test_finds_claude_child(self) -> None:
        assert _check_child_processes(PS_OUTPUT, 57697) is True

    def test_no_claude_child(self) -> None:
        assert _check_child_processes(PS_OUTPUT, 12345) is False

    def test_nonexistent_pid(self) -> None:
        assert _check_child_processes(PS_OUTPUT, 99999) is False


class TestListAllPanes:
    @patch("cc_monitor.discovery.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout=TMUX_OUTPUT)
        panes = list_all_panes()
        assert len(panes) == 6
        mock_run.assert_called_once()

    @patch("cc_monitor.discovery.subprocess.run")
    def test_tmux_not_running(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="no server running"
        )
        assert list_all_panes() == []


class TestVerifyClaudeCandidate:
    @patch("cc_monitor.discovery.subprocess.run")
    def test_verified(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout=PS_OUTPUT)
        assert verify_claude_candidate(57697) is True

    @patch("cc_monitor.discovery.subprocess.run")
    def test_not_verified(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout=PS_OUTPUT)
        assert verify_claude_candidate(12345) is False

    @patch("cc_monitor.discovery.subprocess.run")
    def test_ps_fails(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert verify_claude_candidate(57697) is False


class TestDiscoverSessions:
    @patch("cc_monitor.discovery.subprocess.run")
    def test_discovers_claude_and_opencode(self, mock_run: MagicMock) -> None:
        def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
            if cmd[0] == "tmux":
                return MagicMock(returncode=0, stdout=TMUX_OUTPUT)
            if cmd[0] == "ps":
                return MagicMock(returncode=0, stdout=PS_OUTPUT)
            return MagicMock(returncode=1, stdout="")

        mock_run.side_effect = side_effect
        sessions = discover_sessions()

        claude_sessions = [s for s in sessions if s.agent_type == "claude"]
        opencode_sessions = [s for s in sessions if s.agent_type == "opencode"]

        assert len(claude_sessions) == 2
        assert len(opencode_sessions) == 2

        assert claude_sessions[0].session_name == "writer-cc"
        assert claude_sessions[0].tmux_target == "writer-cc:1.0"
        assert claude_sessions[0].pane_pid == 57697
        assert claude_sessions[0].state == "idle"
        assert claude_sessions[0].summary == ""

        assert opencode_sessions[0].session_name == "agents-py"
        assert opencode_sessions[0].tmux_target == "agents-py:2.1"

    @patch("cc_monitor.discovery.subprocess.run")
    def test_no_tmux(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert discover_sessions() == []

    @patch("cc_monitor.discovery.subprocess.run")
    def test_version_pane_without_claude_child_excluded(
        self, mock_run: MagicMock
    ) -> None:
        tmux_out = "mysession:0.0 3.0.1 11111\n"
        ps_out = "  PID  PPID COMM\n11112 11111 node\n"

        def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
            if cmd[0] == "tmux":
                return MagicMock(returncode=0, stdout=tmux_out)
            return MagicMock(returncode=0, stdout=ps_out)

        mock_run.side_effect = side_effect
        sessions = discover_sessions()
        assert sessions == []
