from __future__ import annotations

from unittest.mock import MagicMock, patch

from rich.table import Table

from cc_monitor.models import AgentSession
from cc_monitor.watch import _build_table, _detect_transitions, _notify, watch_loop


def _make_session(**kwargs: object) -> AgentSession:
    defaults: dict[str, object] = {
        "session_name": "main",
        "window_index": 0,
        "pane_index": 0,
        "agent_type": "claude",
        "state": "working",
        "summary": "editing file",
        "pane_pid": 123,
        "tmux_target": "main:0.0",
    }
    defaults.update(kwargs)
    return AgentSession(**defaults)  # type: ignore[arg-type]


class TestBuildTable:
    def test_empty_sessions(self) -> None:
        table = _build_table([])
        assert isinstance(table, Table)
        assert table.row_count == 0

    def test_single_session(self) -> None:
        sessions = [_make_session()]
        table = _build_table(sessions)
        assert table.row_count == 1

    def test_multiple_sessions(self) -> None:
        sessions = [
            _make_session(tmux_target="main:0.0"),
            _make_session(tmux_target="main:0.1", state="idle"),
        ]
        table = _build_table(sessions)
        assert table.row_count == 2

    def test_table_has_title(self) -> None:
        table = _build_table([])
        assert table.title is not None
        assert "watch" in table.title.lower()


class TestWatchLoop:
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_exits_on_keyboard_interrupt(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=1.0)
        except KeyboardInterrupt:
            pass
        mock_discover.assert_called_once()
        mock_analyze.assert_called_once()
        mock_sleep.assert_called_once_with(1.0)

    @patch("cc_monitor.watch.time.sleep", side_effect=[None, KeyboardInterrupt])
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_loops_until_interrupt(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=2.0)
        except KeyboardInterrupt:
            pass
        assert mock_discover.call_count == 2
        assert mock_analyze.call_count == 2

    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_live_update_called(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        session = _make_session()
        mock_discover.return_value = [session]
        mock_analyze.return_value = [session]
        try:
            watch_loop(interval=1.0)
        except KeyboardInterrupt:
            pass
        mock_discover.assert_called_once()

    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_custom_interval(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=5.0)
        except KeyboardInterrupt:
            pass
        mock_sleep.assert_called_once_with(5.0)


class TestDetectTransitions:
    def test_no_transitions_when_empty(self) -> None:
        assert _detect_transitions([], []) == []

    def test_no_transition_when_state_unchanged(self) -> None:
        prev = [_make_session(state="needs_input", tmux_target="s:0.0")]
        curr = [_make_session(state="needs_input", tmux_target="s:0.0")]
        assert _detect_transitions(prev, curr) == []

    def test_detects_new_needs_input(self) -> None:
        prev = [_make_session(state="working", tmux_target="s:0.0")]
        curr = [_make_session(state="needs_input", tmux_target="s:0.0")]
        assert _detect_transitions(prev, curr) == ["s:0.0"]

    def test_detects_multiple_transitions(self) -> None:
        prev = [
            _make_session(state="working", tmux_target="s:0.0"),
            _make_session(state="idle", tmux_target="s:0.1"),
        ]
        curr = [
            _make_session(state="needs_input", tmux_target="s:0.0"),
            _make_session(state="needs_input", tmux_target="s:0.1"),
        ]
        result = _detect_transitions(prev, curr)
        assert sorted(result) == ["s:0.0", "s:0.1"]

    def test_no_transition_for_non_needs_input(self) -> None:
        prev = [_make_session(state="working", tmux_target="s:0.0")]
        curr = [_make_session(state="idle", tmux_target="s:0.0")]
        assert _detect_transitions(prev, curr) == []

    def test_new_session_with_needs_input(self) -> None:
        prev: list[AgentSession] = []
        curr = [_make_session(state="needs_input", tmux_target="s:0.0")]
        assert _detect_transitions(prev, curr) == ["s:0.0"]


class TestNotify:
    @patch("cc_monitor.watch.subprocess.run")
    @patch("cc_monitor.watch.shutil.which", return_value="/usr/local/bin/terminal-notifier")
    def test_uses_terminal_notifier_when_available(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        result = _notify("Test Title", "Test Message")
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "/usr/local/bin/terminal-notifier"
        assert "-title" in args
        assert "Test Title" in args
        assert "-message" in args
        assert "Test Message" in args

    @patch("cc_monitor.watch.subprocess.run")
    @patch("cc_monitor.watch.shutil.which", side_effect=lambda cmd: "/usr/bin/osascript" if cmd == "osascript" else None)
    def test_falls_back_to_osascript(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        result = _notify("Title", "Msg")
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "/usr/bin/osascript"

    @patch("cc_monitor.watch.shutil.which", return_value=None)
    def test_returns_false_when_no_backend(self, mock_which: MagicMock) -> None:
        result = _notify("Title", "Msg")
        assert result is False


class TestWatchLoopNotify:
    @patch("cc_monitor.watch._notify")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_notify_called_on_transition(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        session = _make_session(state="needs_input", tmux_target="s:0.0")
        mock_discover.return_value = [session]
        mock_analyze.return_value = [session]
        try:
            watch_loop(interval=1.0, notify=True)
        except KeyboardInterrupt:
            pass
        mock_notify.assert_called_once_with("CCM: Input Needed", "s:0.0 needs input")

    @patch("cc_monitor.watch._notify")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_no_notify_when_flag_off(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=1.0, notify=False)
        except KeyboardInterrupt:
            pass
        mock_notify.assert_not_called()
