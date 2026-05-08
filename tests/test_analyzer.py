from __future__ import annotations

from unittest.mock import MagicMock, patch

from cc_monitor.analyzer import (
    _regex_detect_claude,
    _regex_detect_opencode,
    _regex_detect_state,
    _regex_summarize,
    analyze_sessions,
    capture_pane,
)
from cc_monitor.models import AgentSession

CLAUDE_IDLE_PANE = """\
✻ Worked for 9m 26s

  I've completed the refactoring of the auth module. All tests pass and the
  types are clean.

❯
───────────────────────────
  [████████████████░░░░████] $1.430
  ⏵⏵ bypass permissions on (shift+tab to cycle)
""".strip().splitlines()

CLAUDE_WORKING_PANE = """\
  Let me check the implementation.

⏺ Read(src/cc_monitor/discovery.py)
  ⎿  from __future__ import annotations
     import re
     import subprocess

⏺ Bash(echo "test")
  ⎿ test

""".strip().splitlines()

CLAUDE_NEEDS_INPUT_PANE = """\
  I found 3 issues in the codebase that need attention.

  Here's what I recommend:
  1. Update the type hints
  2. Add missing tests
  3. Fix the import order

❯
───────────────────────────
  [████████████████░░░░████] $0.892
  ⏵⏵ bypass permissions on (shift+tab to cycle)
""".strip().splitlines()

CLAUDE_COOKED_IDLE_PANE = """\
✻ Cooked for 9m 2s

  All changes have been committed and pushed.

❯
───────────────────────────
  [████████████████░░░░████] $2.10
""".strip().splitlines()

CLAUDE_CRUNCHED_IDLE_PANE = """\
✻ Crunched for 31m 36s

  Done with the audit.

❯
───────────────────────────
""".strip().splitlines()

OPENCODE_WORKING_PANE = """\
  I'm currently analyzing the test results and checking for any
  remaining issues in the codebase.

  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 · 3m 53s
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
""".strip().splitlines()

OPENCODE_IDLE_PANE = """\
  The refactoring is complete. All tests pass.

     ▣  Auto-Accept · Claude Opus 4.6

  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                    25.2K (3%) · $0.19  ctrl+p commands
""".strip().splitlines()

OPENCODE_NEEDS_INPUT_PANE = """\
  Do you want me to proceed with the changes?

  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                    25.2K (3%) · $0.19  ctrl+p commands
""".strip().splitlines()


class TestRegexDetectClaudeState:
    def test_idle_with_completion_marker(self) -> None:
        assert _regex_detect_claude(CLAUDE_IDLE_PANE) == "idle"

    def test_idle_cooked_variant(self) -> None:
        assert _regex_detect_claude(CLAUDE_COOKED_IDLE_PANE) == "idle"

    def test_idle_crunched_variant(self) -> None:
        assert _regex_detect_claude(CLAUDE_CRUNCHED_IDLE_PANE) == "idle"

    def test_working_with_tool_calls(self) -> None:
        assert _regex_detect_claude(CLAUDE_WORKING_PANE) == "working"

    def test_needs_input_with_prompt(self) -> None:
        assert _regex_detect_claude(CLAUDE_NEEDS_INPUT_PANE) == "needs_input"

    def test_empty_lines(self) -> None:
        assert _regex_detect_claude([]) == "idle"

    def test_prompt_only(self) -> None:
        lines = ["❯ "]
        assert _regex_detect_claude(lines) == "needs_input"

    def test_tool_call_with_prompt_at_bottom(self) -> None:
        lines = [
            "⏺ Read(file.py)",
            "  ⎿  contents",
            "",
            "Done reading.",
            "❯ ",
            "───────────────────────────",
            "  [████████████████░░░░████] $0.50",
        ]
        assert _regex_detect_claude(lines) == "needs_input"


class TestRegexDetectOpenCodeState:
    def test_working_with_timer(self) -> None:
        assert _regex_detect_opencode(OPENCODE_WORKING_PANE) == "working"

    def test_idle_with_done_marker(self) -> None:
        assert _regex_detect_opencode(OPENCODE_IDLE_PANE) == "idle"

    def test_empty_lines(self) -> None:
        assert _regex_detect_opencode([]) == "idle"

    def test_timer_pattern_variations(self) -> None:
        lines = [
            "  ┃  Auto-Accept · Claude Opus 4.6 · 12m 5s",
            "  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
        ]
        assert _regex_detect_opencode(lines) == "working"

    def test_no_timer_no_done_means_needs_input(self) -> None:
        assert _regex_detect_opencode(OPENCODE_NEEDS_INPUT_PANE) == "needs_input"


class TestRegexDetectState:
    def test_dispatches_to_claude(self) -> None:
        assert _regex_detect_state("claude", CLAUDE_WORKING_PANE) == "working"
        assert _regex_detect_state("claude", CLAUDE_NEEDS_INPUT_PANE) == "needs_input"
        assert _regex_detect_state("claude", CLAUDE_IDLE_PANE) == "idle"

    def test_dispatches_to_opencode(self) -> None:
        assert _regex_detect_state("opencode", OPENCODE_WORKING_PANE) == "working"
        assert _regex_detect_state("opencode", OPENCODE_IDLE_PANE) == "idle"

    def test_unknown_agent_returns_idle(self) -> None:
        assert _regex_detect_state("unknown", ["some content"]) == "idle"


class TestCapturePaneIntegration:
    @patch("cc_monitor.analyzer.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="line1\nline2\nline3\n")
        result = capture_pane("session:0.0")
        assert result == "line1\nline2\nline3\n"
        mock_run.assert_called_once_with(
            ["tmux", "capture-pane", "-p", "-t", "session:0.0"],
            capture_output=True,
            text=True,
        )

    @patch("cc_monitor.analyzer.subprocess.run")
    def test_failure_returns_empty(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert capture_pane("bad:target") == ""


class TestRegexSummarize:
    def test_returns_last_meaningful_line(self) -> None:
        lines = ["", "  Some meaningful output here.", "", "───────"]
        result = _regex_summarize("claude", lines)
        assert result == "Some meaningful output here."

    def test_empty_lines(self) -> None:
        assert _regex_summarize("claude", []) == ""

    def test_truncates_long_lines(self) -> None:
        lines = ["x" * 200]
        result = _regex_summarize("claude", lines)
        assert len(result) == 80


class TestAnalyzeSessions:
    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=False)
    @patch("cc_monitor.analyzer.capture_pane")
    def test_regex_fallback(self, mock_capture: MagicMock, _mock_llm: MagicMock) -> None:
        mock_capture.return_value = "\n".join(CLAUDE_WORKING_PANE) + "\n"
        session = AgentSession(
            session_name="test",
            window_index=0,
            pane_index=0,
            agent_type="claude",
            state="idle",
            summary="",
            pane_pid=1234,
            tmux_target="test:0.0",
        )
        result = analyze_sessions([session])
        assert len(result) == 1
        assert result[0].state == "working"

    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=False)
    @patch("cc_monitor.analyzer.capture_pane")
    def test_handles_empty_capture(self, mock_capture: MagicMock, _mock_llm: MagicMock) -> None:
        mock_capture.return_value = ""
        session = AgentSession(
            session_name="test",
            window_index=0,
            pane_index=0,
            agent_type="claude",
            state="idle",
            summary="",
            pane_pid=1234,
            tmux_target="test:0.0",
        )
        result = analyze_sessions([session])
        assert result[0].state == "idle"
        assert result[0].summary == ""

    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=False)
    @patch("cc_monitor.analyzer.capture_pane")
    def test_multiple_sessions(self, mock_capture: MagicMock, _mock_llm: MagicMock) -> None:
        mock_capture.side_effect = [
            "\n".join(CLAUDE_NEEDS_INPUT_PANE) + "\n",
            "\n".join(OPENCODE_WORKING_PANE) + "\n",
        ]
        sessions = [
            AgentSession(
                session_name="s1",
                window_index=0,
                pane_index=0,
                agent_type="claude",
                state="idle",
                summary="",
                pane_pid=100,
                tmux_target="s1:0.0",
            ),
            AgentSession(
                session_name="s2",
                window_index=1,
                pane_index=0,
                agent_type="opencode",
                state="idle",
                summary="",
                pane_pid=200,
                tmux_target="s2:1.0",
            ),
        ]
        result = analyze_sessions(sessions)
        assert result[0].state == "needs_input"
        assert result[1].state == "working"
