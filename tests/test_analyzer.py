from __future__ import annotations

import hashlib

from unittest.mock import MagicMock, patch

from cc_monitor.analyzer import (
    _regex_detect_claude,
    _regex_detect_opencode,
    _regex_detect_state,
    _regex_summarize,
    analyze_sessions,
    capture_pane,
)
from cc_monitor.llm_provider import LLMResult
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
    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=set())
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

    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=set())
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

    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=set())
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


def _make_session(tmux_target: str = "test:0.0", **kwargs: object) -> AgentSession:
    defaults: dict[str, object] = {
        "session_name": "test",
        "window_index": 0,
        "pane_index": 0,
        "agent_type": "claude",
        "state": "idle",
        "summary": "",
        "pane_pid": 1234,
        "tmux_target": tmux_target,
    }
    defaults.update(kwargs)
    return AgentSession(**defaults)  # type: ignore[arg-type]


PANE_CONTENT_A = "line1\nline2\nline3\n"
PANE_CONTENT_B = "line1\nline2\nchanged\n"


def _hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def _llm_succeed_all(
    sessions: list[AgentSession], pane_contents: dict[str, str]
) -> set[str]:
    """Mock side effect: return all tmux_targets as succeeded."""
    return {s.tmux_target for s in sessions}


class TestCacheMiss:
    @patch("cc_monitor.analyzer._analyze_with_llm", side_effect=_llm_succeed_all)
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_A)
    def test_first_call_is_cache_miss(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """First call with empty cache should call LLM."""
        cache: dict[str, tuple[str, LLMResult]] = {}
        session = _make_session()
        analyze_sessions([session], cache=cache)
        mock_llm.assert_called_once()

    @patch("cc_monitor.analyzer._analyze_with_llm")
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_A)
    def test_cache_stores_result_after_llm(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """After LLM succeeds, result is stored in cache."""
        cache: dict[str, tuple[str, LLMResult]] = {}
        session = _make_session()

        def llm_side_effect(
            sessions: list[AgentSession], pane_contents: dict[str, str]
        ) -> set[str]:
            for s in sessions:
                s.state = "working"
                s.summary = "doing stuff"
            return {s.tmux_target for s in sessions}

        mock_llm.side_effect = llm_side_effect
        analyze_sessions([session], cache=cache)
        assert "test:0.0" in cache
        stored_hash, stored_result = cache["test:0.0"]
        assert stored_hash == _hash(PANE_CONTENT_A)
        assert stored_result.state == "working"
        assert stored_result.summary == "doing stuff"


class TestCacheHit:
    @patch("cc_monitor.analyzer._analyze_with_llm", side_effect=_llm_succeed_all)
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_A)
    def test_cache_hit_skips_llm(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """Second call with same content should skip LLM."""
        content_hash = _hash(PANE_CONTENT_A)
        cached_result = LLMResult(state="working", summary="cached summary")
        cache: dict[str, tuple[str, LLMResult]] = {
            "test:0.0": (content_hash, cached_result),
        }
        session = _make_session()
        result = analyze_sessions([session], cache=cache)
        mock_llm.assert_not_called()
        assert result[0].state == "working"
        assert result[0].summary == "cached summary"


class TestCacheContentChange:
    @patch("cc_monitor.analyzer._analyze_with_llm", side_effect=_llm_succeed_all)
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_B)
    def test_content_change_causes_cache_miss(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """Changed content should miss cache and call LLM."""
        old_hash = _hash(PANE_CONTENT_A)
        cached_result = LLMResult(state="working", summary="old summary")
        cache: dict[str, tuple[str, LLMResult]] = {
            "test:0.0": (old_hash, cached_result),
        }
        session = _make_session()
        analyze_sessions([session], cache=cache)
        mock_llm.assert_called_once()


class TestCacheNone:
    @patch("cc_monitor.analyzer._analyze_with_llm", side_effect=_llm_succeed_all)
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_A)
    def test_no_cache_always_calls_llm(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """cache=None (status mode) should always call LLM."""
        session = _make_session()
        analyze_sessions([session], cache=None)
        mock_llm.assert_called_once()

    @patch("cc_monitor.analyzer._analyze_with_llm", side_effect=_llm_succeed_all)
    @patch("cc_monitor.analyzer.capture_pane", return_value=PANE_CONTENT_A)
    def test_no_cache_default_param(
        self, _mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """Default cache param (None) should always call LLM."""
        session = _make_session()
        analyze_sessions([session])
        mock_llm.assert_called_once()


class TestCacheRegexFallback:
    @patch("cc_monitor.analyzer._analyze_with_llm", return_value=set())
    @patch("cc_monitor.analyzer.capture_pane")
    def test_regex_fallback_ignores_cache(
        self, mock_capture: MagicMock, _mock_llm: MagicMock
    ) -> None:
        """Regex fallback should run even when cache is provided."""
        content = "\n".join(CLAUDE_WORKING_PANE) + "\n"
        mock_capture.return_value = content
        cached_result = LLMResult(state="idle", summary="stale cached")
        # Pre-populate cache with different hash to force miss -> LLM fails -> regex
        cache: dict[str, tuple[str, LLMResult]] = {
            "test:0.0": ("different_hash", cached_result),
        }
        session = _make_session()
        result = analyze_sessions([session], cache=cache)
        # Regex should classify as working, not use cached "idle"
        assert result[0].state == "working"


class TestPartialLLMFailureCache:
    @patch("cc_monitor.analyzer._analyze_with_llm")
    @patch("cc_monitor.analyzer.capture_pane")
    def test_only_successful_session_is_cached(
        self, mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """When LLM succeeds for A but fails for B, only A is cached."""
        mock_capture.side_effect = [PANE_CONTENT_A, PANE_CONTENT_B]
        session_a = _make_session("a:0.0")
        session_b = _make_session("b:0.0")

        def llm_side_effect(
            sessions: list[AgentSession], pane_contents: dict[str, str]
        ) -> set[str]:
            for s in sessions:
                if s.tmux_target == "a:0.0":
                    s.state = "working"
                    s.summary = "building feature"
                # b:0.0 is not touched — simulates LLM failure
            return {"a:0.0"}  # only A succeeded

        mock_llm.side_effect = llm_side_effect
        cache: dict[str, tuple[str, LLMResult]] = {}
        analyze_sessions([session_a, session_b], cache=cache)

        # A should be cached
        assert "a:0.0" in cache
        assert cache["a:0.0"][1].state == "working"
        assert cache["a:0.0"][1].summary == "building feature"

        # B should NOT be cached (LLM failed for it)
        assert "b:0.0" not in cache

        # B should have fallen back to regex
        assert session_b.state != "idle" or session_b.summary != ""


class TestEmptyCaptureNotCached:
    @patch("cc_monitor.analyzer._analyze_with_llm")
    @patch("cc_monitor.analyzer.capture_pane")
    def test_empty_content_not_cached(
        self, mock_capture: MagicMock, mock_llm: MagicMock
    ) -> None:
        """Empty capture_pane content should not be stored in cache."""
        mock_capture.return_value = ""
        session = _make_session()

        def llm_side_effect(
            sessions: list[AgentSession], pane_contents: dict[str, str]
        ) -> set[str]:
            for s in sessions:
                s.state = "idle"
                s.summary = ""
            return {s.tmux_target for s in sessions}

        mock_llm.side_effect = llm_side_effect
        cache: dict[str, tuple[str, LLMResult]] = {}
        analyze_sessions([session], cache=cache)

        # Should NOT be cached because content was empty
        assert "test:0.0" not in cache
