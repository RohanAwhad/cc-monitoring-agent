from __future__ import annotations

from unittest.mock import MagicMock, patch

from cc_monitor.analyzer import (
    capture_pane,
    detect_claude_state,
    detect_opencode_state,
    detect_state,
)

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

  ┃
  ┃
  ┃
  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max
  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                    25.2K (3%) · $0.19  ctrl+p commands
""".strip().splitlines()


class TestDetectClaudeState:
    def test_idle_with_completion_marker(self) -> None:
        assert detect_claude_state(CLAUDE_IDLE_PANE) == "idle"

    def test_idle_cooked_variant(self) -> None:
        assert detect_claude_state(CLAUDE_COOKED_IDLE_PANE) == "idle"

    def test_working_with_tool_calls(self) -> None:
        assert detect_claude_state(CLAUDE_WORKING_PANE) == "working"

    def test_needs_input_with_prompt(self) -> None:
        assert detect_claude_state(CLAUDE_NEEDS_INPUT_PANE) == "needs_input"

    def test_empty_lines(self) -> None:
        assert detect_claude_state([]) == "idle"

    def test_prompt_only(self) -> None:
        lines = ["❯ "]
        assert detect_claude_state(lines) == "needs_input"

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
        assert detect_claude_state(lines) == "needs_input"


class TestDetectOpenCodeState:
    def test_working_with_timer(self) -> None:
        assert detect_opencode_state(OPENCODE_WORKING_PANE) == "working"

    def test_idle_no_timer(self) -> None:
        assert detect_opencode_state(OPENCODE_IDLE_PANE) == "needs_input"

    def test_empty_lines(self) -> None:
        assert detect_opencode_state([]) == "idle"

    def test_timer_pattern_variations(self) -> None:
        lines = [
            "  ┃  Auto-Accept · Claude Opus 4.6 · 12m 5s",
            "  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
        ]
        assert detect_opencode_state(lines) == "working"

    def test_no_timer_means_idle(self) -> None:
        lines = [
            "  ┃  Auto-Accept · Claude Opus 4.6 Vertex (Anthropic) · max",
            "  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
            "                                    25.2K (3%) · $0.19  ctrl+p commands",
        ]
        assert detect_opencode_state(lines) == "needs_input"


class TestDetectState:
    def test_dispatches_to_claude(self) -> None:
        assert detect_state("claude", CLAUDE_WORKING_PANE) == "working"
        assert detect_state("claude", CLAUDE_NEEDS_INPUT_PANE) == "needs_input"
        assert detect_state("claude", CLAUDE_IDLE_PANE) == "idle"

    def test_dispatches_to_opencode(self) -> None:
        assert detect_state("opencode", OPENCODE_WORKING_PANE) == "working"
        assert detect_state("opencode", OPENCODE_IDLE_PANE) == "needs_input"

    def test_unknown_agent_returns_idle(self) -> None:
        assert detect_state("unknown", ["some content"]) == "idle"


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
