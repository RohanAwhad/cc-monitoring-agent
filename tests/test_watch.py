from __future__ import annotations

from unittest.mock import MagicMock, patch

from rich.table import Table

from cc_monitor.models import AgentSession
from cc_monitor.watch import _build_table, watch_loop


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

    @patch("cc_monitor.watch.time.sleep", side_effect=KeyboardInterrupt)
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_passes_cache_to_analyze(
        self,
        _mock_discover: MagicMock,
        mock_analyze: MagicMock,
        _mock_sleep: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=1.0)
        except KeyboardInterrupt:
            pass
        mock_analyze.assert_called_once()
        _, kwargs = mock_analyze.call_args
        assert "cache" in kwargs
        assert isinstance(kwargs["cache"], dict)

    @patch("cc_monitor.watch.time.sleep", side_effect=[None, KeyboardInterrupt])
    @patch("cc_monitor.watch.analyze_sessions", return_value=[])
    @patch("cc_monitor.watch.discover_sessions", return_value=[])
    def test_cache_persists_across_iterations(
        self,
        _mock_discover: MagicMock,
        mock_analyze: MagicMock,
        _mock_sleep: MagicMock,
    ) -> None:
        try:
            watch_loop(interval=1.0)
        except KeyboardInterrupt:
            pass
        assert mock_analyze.call_count == 2
        # Both calls should receive the same cache dict instance
        cache_1 = mock_analyze.call_args_list[0][1]["cache"]
        cache_2 = mock_analyze.call_args_list[1][1]["cache"]
        assert cache_1 is cache_2
