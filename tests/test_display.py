from __future__ import annotations

from cc_monitor.display import display_results, format_summary_line
from cc_monitor.models import AgentSession


def _make_session(
    tmux_target: str = "main:0.0",
    agent_type: str = "claude",
    state: str = "working",
    summary: str = "Using Read",
) -> AgentSession:
    parts = tmux_target.split(":")
    session_name = parts[0]
    wp = parts[1].split(".")
    return AgentSession(
        session_name=session_name,
        window_index=int(wp[0]),
        pane_index=int(wp[1]),
        agent_type=agent_type,  # type: ignore[arg-type]
        state=state,  # type: ignore[arg-type]
        summary=summary,
        pane_pid=1234,
        tmux_target=tmux_target,
    )


class TestDisplayResults:
    def test_empty_sessions(self, capsys: object) -> None:
        display_results([])
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "No agent sessions found" in captured.out

    def test_single_session_does_not_crash(self) -> None:
        sessions = [_make_session()]
        display_results(sessions)

    def test_multiple_sessions(self) -> None:
        sessions = [
            _make_session(
                tmux_target="dev:0.0", agent_type="claude", state="idle", summary="Done"
            ),
            _make_session(
                tmux_target="work:1.0",
                agent_type="opencode",
                state="needs_input",
                summary="Waiting for input",
            ),
            _make_session(
                tmux_target="build:2.1",
                agent_type="claude",
                state="working",
                summary="Using Bash",
            ),
        ]
        display_results(sessions)

    def test_output_contains_session_data(self, capsys: object) -> None:
        sessions = [
            _make_session(
                tmux_target="myproj:3.2",
                agent_type="claude",
                state="working",
                summary="Using Edit",
            ),
        ]
        display_results(sessions)
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "myproj:3.2" in captured.out
        assert "claude" in captured.out
        assert "working" in captured.out
        assert "Using Edit" in captured.out

    def test_all_states_render(self) -> None:
        sessions = [
            _make_session(state="idle", summary="Idle"),
            _make_session(state="working", summary="Working"),
            _make_session(state="needs_input", summary="Needs input"),
        ]
        display_results(sessions)


class TestFormatSummaryLine:
    def test_zero_sessions(self) -> None:
        result = format_summary_line([])
        assert result == "0 agents:"

    def test_single_session(self) -> None:
        sessions = [_make_session(state="working")]
        result = format_summary_line(sessions)
        assert result == "1 agents:, 1 working"

    def test_multiple_sessions_multiple_states(self) -> None:
        sessions = [
            _make_session(state="working", tmux_target="a:0.0"),
            _make_session(state="idle", tmux_target="b:0.0"),
            _make_session(state="working", tmux_target="c:0.0"),
        ]
        result = format_summary_line(sessions)
        assert result == "3 agents:, 1 idle, 2 working"

    def test_no_ansi_codes(self) -> None:
        sessions = [_make_session(state="idle")]
        result = format_summary_line(sessions)
        assert "\x1b" not in result
        assert "[" not in result
