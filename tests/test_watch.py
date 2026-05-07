from __future__ import annotations

from unittest.mock import MagicMock, patch

from rich.table import Table

from cc_monitor.models import AgentSession
from cc_monitor.watch import (
    _build_table,
    detect_state_changes,
    send_notification,
    watch_loop,
)


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


class TestDetectStateChanges:
    def test_no_changes(self) -> None:
        prev = {"main:0.0": "working", "main:0.1": "idle"}
        curr = {"main:0.0": "working", "main:0.1": "idle"}
        assert detect_state_changes(prev, curr) == []

    def test_state_transition_detected(self) -> None:
        prev = {"main:0.0": "working"}
        curr = {"main:0.0": "needs_input"}
        changes = detect_state_changes(prev, curr)
        assert len(changes) == 1
        assert changes[0] == ("main:0.0", "working", "needs_input")

    def test_new_session_not_reported(self) -> None:
        prev: dict[str, str] = {}
        curr = {"main:0.0": "needs_input"}
        assert detect_state_changes(prev, curr) == []

    def test_multiple_changes(self) -> None:
        prev = {"main:0.0": "working", "main:0.1": "idle"}
        curr = {"main:0.0": "needs_input", "main:0.1": "working"}
        changes = detect_state_changes(prev, curr)
        assert len(changes) == 2

    def test_disappeared_session_not_reported(self) -> None:
        prev = {"main:0.0": "working", "main:0.1": "idle"}
        curr = {"main:0.0": "working"}
        assert detect_state_changes(prev, curr) == []


class TestSendNotification:
    @patch("cc_monitor.watch.subprocess.run")
    def test_calls_osascript(self, mock_run: MagicMock) -> None:
        send_notification("Test Title", "Test Message")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "osascript"
        assert args[1] == "-e"
        assert "Test Title" in args[2]
        assert "Test Message" in args[2]


class TestWatchLoopNotify:
    @patch("cc_monitor.watch.send_notification")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_no_notification_on_first_scan(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        session = _make_session(state="needs_input")
        mock_discover.return_value = [session]
        mock_analyze.return_value = [session]
        try:
            watch_loop(interval=1.0, notify=True)
        except KeyboardInterrupt:
            pass
        mock_notify.assert_not_called()

    @patch("cc_monitor.watch.send_notification")
    @patch("cc_monitor.watch.time.sleep", side_effect=[None, KeyboardInterrupt])
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_notification_on_needs_input_transition(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        session_working = _make_session(state="working")
        session_needs_input = _make_session(state="needs_input")
        mock_discover.side_effect = [[session_working], [session_needs_input]]
        mock_analyze.side_effect = [[session_working], [session_needs_input]]
        try:
            watch_loop(interval=1.0, notify=True)
        except KeyboardInterrupt:
            pass
        mock_notify.assert_called_once_with(
            "CCM: Input Needed",
            "main:0.0 changed from working to needs_input",
        )

    @patch("cc_monitor.watch.send_notification")
    @patch("cc_monitor.watch.time.sleep", side_effect=[None, KeyboardInterrupt])
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_no_notification_on_other_transitions(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        session_working = _make_session(state="working")
        session_idle = _make_session(state="idle")
        mock_discover.side_effect = [[session_working], [session_idle]]
        mock_analyze.side_effect = [[session_working], [session_idle]]
        try:
            watch_loop(interval=1.0, notify=True)
        except KeyboardInterrupt:
            pass
        mock_notify.assert_not_called()

    @patch("cc_monitor.watch.send_notification")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_no_notification_when_notify_false(
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
