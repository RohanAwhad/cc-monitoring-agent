from __future__ import annotations

import json
import sys
from unittest.mock import patch

from cc_monitor.cli import main


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_main_runs(mock_panes: object, monkeypatch: object) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_json_output(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_help(mock_panes: object, monkeypatch: object, capsys: object) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "--help"])  # type: ignore[attr-defined]
    try:
        main()
    except SystemExit:
        pass
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "usage" in captured.out.lower() or "ccm" in captured.out


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_status_subcommand(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_bare_ccm_defaults_to_status(
    mock_panes: object, monkeypatch: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm"])  # type: ignore[attr-defined]
    main()


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_bare_ccm_json_backward_compat(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_summary_zero_agents(
    mock_panes: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "summary"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert captured.out == "0 agents"


@patch("cc_monitor.cli.discover_sessions")
@patch("cc_monitor.cli.analyze_sessions")
def test_summary_mixed_states(
    mock_analyze: object,
    mock_discover: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    from cc_monitor.models import AgentSession

    sessions = [
        AgentSession(
            session_name="s1",
            window_index=0,
            pane_index=0,
            agent_type="claude",
            state="working",
            summary="",
            pane_pid=1,
            tmux_target="s1:0.0",
        ),
        AgentSession(
            session_name="s2",
            window_index=0,
            pane_index=0,
            agent_type="claude",
            state="working",
            summary="",
            pane_pid=2,
            tmux_target="s2:0.0",
        ),
        AgentSession(
            session_name="s3",
            window_index=0,
            pane_index=0,
            agent_type="claude",
            state="idle",
            summary="",
            pane_pid=3,
            tmux_target="s3:0.0",
        ),
    ]
    mock_discover.return_value = sessions  # type: ignore[attr-defined]
    mock_analyze.return_value = sessions  # type: ignore[attr-defined]
    monkeypatch.setattr(sys, "argv", ["ccm", "summary"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    out = captured.out
    assert out.startswith("3 agents: ")
    assert "2 working" in out
    assert "1 idle" in out
    assert "\x1b" not in out


@patch("cc_monitor.cli.discover_sessions")
@patch("cc_monitor.cli.analyze_sessions")
def test_summary_no_trailing_newline(
    mock_analyze: object,
    mock_discover: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    mock_discover.return_value = []  # type: ignore[attr-defined]
    mock_analyze.return_value = []  # type: ignore[attr-defined]
    monkeypatch.setattr(sys, "argv", ["ccm", "summary"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert not captured.out.endswith("\n")
