from __future__ import annotations

from unittest.mock import MagicMock, call, patch

from rich.table import Table

from cc_monitor.models import AgentSession
from cc_monitor.watch import _build_table, _detect_transitions, _send_desktop_alert, watch_loop


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

    @patch("cc_monitor.watch._send_desktop_alert")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_notify_fires_on_needs_input(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_alert: MagicMock,
    ) -> None:
        session = _make_session(state="needs_input")
        mock_discover.return_value = [session]
        mock_analyze.return_value = [session]
        try:
            watch_loop(interval=1.0, notify=True)
        except KeyboardInterrupt:
            pass
        mock_alert.assert_called_once_with(
            "CCM: Input Required",
            "Session main:0.0 needs your input",
        )

    @patch("cc_monitor.watch._send_desktop_alert")
    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions")
    @patch("cc_monitor.watch.discover_sessions")
    def test_notify_not_fired_when_disabled(
        self,
        mock_discover: MagicMock,
        mock_analyze: MagicMock,
        mock_sleep: MagicMock,
        mock_alert: MagicMock,
    ) -> None:
        session = _make_session(state="needs_input")
        mock_discover.return_value = [session]
        mock_analyze.return_value = [session]
        try:
            watch_loop(interval=1.0, notify=False)
        except KeyboardInterrupt:
            pass
        mock_alert.assert_not_called()


class TestDetectTransitions:
    def test_no_previous_state(self) -> None:
        current = {"main:0.0": "needs_input"}
        result = _detect_transitions({}, current)
        assert result == ["main:0.0"]

    def test_transition_to_needs_input(self) -> None:
        previous = {"main:0.0": "working"}
        current = {"main:0.0": "needs_input"}
        result = _detect_transitions(previous, current)
        assert result == ["main:0.0"]

    def test_already_needs_input_no_transition(self) -> None:
        previous = {"main:0.0": "needs_input"}
        current = {"main:0.0": "needs_input"}
        result = _detect_transitions(previous, current)
        assert result == []

    def test_transition_away_from_needs_input(self) -> None:
        previous = {"main:0.0": "needs_input"}
        current = {"main:0.0": "working"}
        result = _detect_transitions(previous, current)
        assert result == []

    def test_multiple_sessions_mixed(self) -> None:
        previous = {"a:0.0": "working", "b:0.0": "needs_input"}
        current = {"a:0.0": "needs_input", "b:0.0": "needs_input", "c:0.0": "needs_input"}
        result = _detect_transitions(previous, current)
        assert sorted(result) == ["a:0.0", "c:0.0"]

    def test_new_session_working(self) -> None:
        current = {"main:0.0": "working"}
        result = _detect_transitions({}, current)
        assert result == []


class TestSendDesktopAlert:
    @patch("cc_monitor.watch.subprocess.run")
    @patch("cc_monitor.watch.shutil.which", return_value="/usr/local/bin/terminal-notifier")
    def test_uses_terminal_notifier_when_available(
        self,
        mock_which: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        _send_desktop_alert("Title", "Body")
        mock_which.assert_called_once_with("terminal-notifier")
        mock_run.assert_called_once_with(
            ["terminal-notifier", "-title", "Title", "-message", "Body"],
            capture_output=True,
        )

    @patch("cc_monitor.watch.subprocess.run")
    @patch("cc_monitor.watch.shutil.which", return_value=None)
    def test_falls_back_to_osascript(
        self,
        mock_which: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        _send_desktop_alert("Title", "Body")
        mock_which.assert_called_once_with("terminal-notifier")
        mock_run.assert_called_once_with(
            ["osascript", "-e", 'display notification "Body" with title "Title"'],
            capture_output=True,
        )
