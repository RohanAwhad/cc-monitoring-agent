from __future__ import annotations

from unittest.mock import MagicMock, patch

from cc_monitor.analyzer import (
    analyze_sessions,
    capture_pane,
    detect_claude_state,
    detect_codex_state,
    detect_gemini_state,
    detect_opencode_state,
    detect_state,
    summarize_activity,
    summarize_claude_activity,
    summarize_codex_activity,
    summarize_gemini_activity,
    summarize_opencode_activity,
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


CLAUDE_RECAP_PANE = """\
  Some previous output here.

※ recap: Building a writing assistance webapp with React frontend
""".strip().splitlines()

CLAUDE_THINKING_PANE = """\
  still thinking...
  Let me analyze this further.
""".strip().splitlines()

CLAUDE_COMPLETION_PANE = """\
✻ Worked for 5m 12s

  All tests pass now.
""".strip().splitlines()


class TestSummarizeClaudeActivity:
    def test_recap_extraction(self) -> None:
        result = summarize_claude_activity(CLAUDE_RECAP_PANE)
        assert result == "Building a writing assistance webapp with React frontend"

    def test_tool_call_extraction(self) -> None:
        result = summarize_claude_activity(CLAUDE_WORKING_PANE)
        assert result == "Using Read"

    def test_thinking_state(self) -> None:
        result = summarize_claude_activity(CLAUDE_THINKING_PANE)
        assert result == "Thinking..."

    def test_completion_marker(self) -> None:
        result = summarize_claude_activity(CLAUDE_COMPLETION_PANE)
        assert result == "Completed 5m 12s ago"

    def test_fallback_last_meaningful_line(self) -> None:
        lines = ["", "  Some meaningful output here.", "", ""]
        result = summarize_claude_activity(lines)
        assert result == "Some meaningful output here."

    def test_empty_lines(self) -> None:
        assert summarize_claude_activity([]) == ""

    def test_decoration_only_lines(self) -> None:
        lines = ["───────────────────────────", "  [████████████████░░░░████]", ""]
        result = summarize_claude_activity(lines)
        assert result == ""


class TestSummarizeOpenCodeActivity:
    def test_working_with_timer(self) -> None:
        result = summarize_opencode_activity(OPENCODE_WORKING_PANE)
        assert "Processing for" in result
        assert "3m 53s" in result

    def test_idle_returns_last_content(self) -> None:
        result = summarize_opencode_activity(OPENCODE_IDLE_PANE)
        assert result == "The refactoring is complete. All tests pass."

    def test_empty_lines(self) -> None:
        assert summarize_opencode_activity([]) == "Active session"

    def test_fallback_active_session(self) -> None:
        lines = ["  ┃", "  ┃", "  ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"]
        result = summarize_opencode_activity(lines)
        assert result == "Active session"


class TestSummarizeActivity:
    def test_dispatches_to_claude(self) -> None:
        result = summarize_activity("claude", CLAUDE_WORKING_PANE)
        assert result == "Using Read"

    def test_dispatches_to_opencode(self) -> None:
        result = summarize_activity("opencode", OPENCODE_WORKING_PANE)
        assert "Processing for" in result

    def test_unknown_agent(self) -> None:
        assert summarize_activity("unknown", ["something"]) == ""


class TestAnalyzeSessions:
    @patch("cc_monitor.analyzer.capture_pane")
    def test_updates_sessions(self, mock_capture: MagicMock) -> None:
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
        assert result[0].summary == "Using Read"

    @patch("cc_monitor.analyzer.capture_pane")
    def test_handles_empty_capture(self, mock_capture: MagicMock) -> None:
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

    @patch("cc_monitor.analyzer.capture_pane")
    def test_multiple_sessions(self, mock_capture: MagicMock) -> None:
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
        assert "Processing for" in result[1].summary


GEMINI_IDLE_PANE = """\
  I've completed the analysis of your codebase.
  Here are the key findings.

gemini>
""".strip().splitlines()

GEMINI_WORKING_PANE = """\
  Let me analyze the authentication module.
  Reading src/auth.py...
  Checking dependencies...
""".strip().splitlines()

CODEX_IDLE_PANE = """\
  All changes have been applied successfully.
  Tests are passing.

codex>
""".strip().splitlines()

CODEX_WORKING_PANE = """\
  Refactoring the database layer.
  Updating models...
  Running migrations...
""".strip().splitlines()


class TestDetectGeminiState:
    def test_idle_with_prompt(self) -> None:
        assert detect_gemini_state(GEMINI_IDLE_PANE) == "needs_input"

    def test_working_no_prompt(self) -> None:
        assert detect_gemini_state(GEMINI_WORKING_PANE) == "working"

    def test_empty_lines(self) -> None:
        assert detect_gemini_state([]) == "idle"


class TestDetectCodexState:
    def test_idle_with_prompt(self) -> None:
        assert detect_codex_state(CODEX_IDLE_PANE) == "needs_input"

    def test_working_no_prompt(self) -> None:
        assert detect_codex_state(CODEX_WORKING_PANE) == "working"

    def test_empty_lines(self) -> None:
        assert detect_codex_state([]) == "idle"


class TestDetectStateGeminiCodex:
    def test_dispatches_to_gemini(self) -> None:
        assert detect_state("gemini", GEMINI_IDLE_PANE) == "needs_input"
        assert detect_state("gemini", GEMINI_WORKING_PANE) == "working"

    def test_dispatches_to_codex(self) -> None:
        assert detect_state("codex", CODEX_IDLE_PANE) == "needs_input"
        assert detect_state("codex", CODEX_WORKING_PANE) == "working"


class TestSummarizeGeminiActivity:
    def test_returns_last_content(self) -> None:
        result = summarize_gemini_activity(GEMINI_WORKING_PANE)
        assert result == "Checking dependencies..."

    def test_empty_lines(self) -> None:
        assert summarize_gemini_activity([]) == "Active session"

    def test_prompt_filtered(self) -> None:
        result = summarize_gemini_activity(GEMINI_IDLE_PANE)
        assert "gemini>" not in result


class TestSummarizeCodexActivity:
    def test_returns_last_content(self) -> None:
        result = summarize_codex_activity(CODEX_WORKING_PANE)
        assert result == "Running migrations..."

    def test_empty_lines(self) -> None:
        assert summarize_codex_activity([]) == "Active session"

    def test_prompt_filtered(self) -> None:
        result = summarize_codex_activity(CODEX_IDLE_PANE)
        assert "codex>" not in result
