from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

from cc_monitor.cli import main

TMUX_OUTPUT = """\
writer-cc:1.0 2.1.119 57697
agents-py:2.1 opencode 95294
dev:0.0 zsh 12345
"""

PS_OUTPUT = """\
  PID  PPID COMM
57698 57697 claude
95295 95294 opencode
12346 12345 zsh
"""

CLAUDE_WORKING_CONTENT = """\
  Let me check the implementation.

⏺ Read(src/cc_monitor/discovery.py)
  ⎿  from __future__ import annotations
     import re
     import subprocess

⏺ Bash(echo "test")
  ⎿ test

"""

OPENCODE_IDLE_CONTENT = """\
  The refactoring is complete. All tests pass.

  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                    25.2K (3%) · $0.19  ctrl+p commands
"""

CLAUDE_NEEDS_INPUT_CONTENT = """\
  I found 3 issues in the codebase that need attention.

  Here's what I recommend:
  1. Update the type hints
  2. Add missing tests
  3. Fix the import order

❯
───────────────────────────
  [████████████████░░░░████] $0.892
  ⏵⏵ bypass permissions on (shift+tab to cycle)
"""


MIXED_TMUX_OUTPUT = """\
writer-cc:1.0 2.1.119 57697
agents-py:2.1 opencode 95294
review:3.0 2.1.120 33333
"""

MIXED_PS_OUTPUT = """\
  PID  PPID COMM
57698 57697 claude
95295 95294 opencode
33334 33333 claude
"""


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


class TestFullPipeline:
    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_discover_analyze_display(
        self, mock_analyzer_run: MagicMock, mock_discovery_run: MagicMock
    ) -> None:
        pane_contents = {
            "writer-cc:1.0": CLAUDE_WORKING_CONTENT,
            "agents-py:2.1": OPENCODE_IDLE_CONTENT,
        }
        effect = _subprocess_side_effect(TMUX_OUTPUT, PS_OUTPUT, pane_contents)
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        from cc_monitor.analyzer import analyze_sessions
        from cc_monitor.discovery import discover_sessions
        from cc_monitor.display import display_results

        sessions = discover_sessions()
        assert len(sessions) == 2

        sessions = analyze_sessions(sessions)

        claude_s = [s for s in sessions if s.agent_type == "claude"][0]
        assert claude_s.state == "working"
        assert "Using Read" in claude_s.summary

        opencode_s = [s for s in sessions if s.agent_type == "opencode"][0]
        assert opencode_s.state == "needs_input"

        display_results(sessions)

    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_mixed_states_json_output(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {
            "writer-cc:1.0": CLAUDE_WORKING_CONTENT,
            "agents-py:2.1": OPENCODE_IDLE_CONTENT,
            "review:3.0": CLAUDE_NEEDS_INPUT_CONTENT,
        }
        effect = _subprocess_side_effect(
            MIXED_TMUX_OUTPUT, MIXED_PS_OUTPUT, pane_contents
        )
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert "sessions" in data
        assert len(data["sessions"]) == 3

        states = {s["tmux_target"]: s["state"] for s in data["sessions"]}
        assert states["writer-cc:1.0"] == "working"
        assert states["agents-py:2.1"] == "needs_input"
        assert states["review:3.0"] == "needs_input"

        types = {s["tmux_target"]: s["agent_type"] for s in data["sessions"]}
        assert types["writer-cc:1.0"] == "claude"
        assert types["agents-py:2.1"] == "opencode"
        assert types["review:3.0"] == "claude"

    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_no_agent_panes_found(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        capsys: object,
    ) -> None:
        tmux_out = "dev:0.0 zsh 12345\nbuild:1.0 vim 99999\n"
        mock_discovery_run.return_value = MagicMock(returncode=0, stdout=tmux_out)

        from cc_monitor.discovery import discover_sessions
        from cc_monitor.display import display_results

        sessions = discover_sessions()
        assert sessions == []

        display_results(sessions)
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "No agent sessions found" in captured.out

    @patch("cc_monitor.discovery.subprocess.run")
    def test_tmux_not_available(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        from cc_monitor.discovery import discover_sessions

        sessions = discover_sessions()
        assert sessions == []


class TestCLIIntegration:
    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_table_output_with_sessions(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {"writer-cc:1.0": CLAUDE_WORKING_CONTENT}
        effect = _subprocess_side_effect(
            "writer-cc:1.0 2.1.119 57697\n", PS_OUTPUT, pane_contents
        )
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "writer-cc:1.0" in captured.out
        assert "claude" in captured.out

    @patch("cc_monitor.discovery.subprocess.run")
    def test_empty_result_exit_code_zero(
        self,
        mock_run: MagicMock,
        monkeypatch: object,
    ) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
        main()

    @patch("cc_monitor.discovery.subprocess.run")
    def test_json_empty_sessions(
        self,
        mock_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json"])  # type: ignore[attr-defined]
        main()
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        assert data == {"sessions": []}

    @patch("cc_monitor.discovery.subprocess.run")
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_json_structure_matches_model(
        self,
        mock_analyzer_run: MagicMock,
        mock_discovery_run: MagicMock,
        monkeypatch: object,
        capsys: object,
    ) -> None:
        pane_contents = {"writer-cc:1.0": CLAUDE_WORKING_CONTENT}
        effect = _subprocess_side_effect(
            "writer-cc:1.0 2.1.119 57697\n", PS_OUTPUT, pane_contents
        )
        mock_discovery_run.side_effect = effect
        mock_analyzer_run.side_effect = effect

        monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json"])  # type: ignore[attr-defined]
        main()

        captured = capsys.readouterr()  # type: ignore[attr-defined]
        data = json.loads(captured.out)
        session = data["sessions"][0]
        expected_keys = {
            "session_name",
            "window_index",
            "pane_index",
            "agent_type",
            "state",
            "summary",
            "pane_pid",
            "tmux_target",
            "cwd",
        }
        assert set(session.keys()) == expected_keys
