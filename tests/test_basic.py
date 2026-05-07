from __future__ import annotations

import json
import sys
from unittest.mock import patch

from cc_monitor.cli import main
from cc_monitor.models import AgentSession


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
def test_bare_ccm_defaults_to_status(mock_panes: object, monkeypatch: object) -> None:
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


def _make_session(
    name: str = "main",
    window: int = 0,
    pane: int = 0,
    agent: str = "claude",
) -> AgentSession:
    return AgentSession(
        session_name=name,
        window_index=window,
        pane_index=pane,
        agent_type=agent,  # type: ignore[arg-type]
        state="idle",
        summary="",
        pane_pid=1000,
        tmux_target=f"{name}:{window}.{pane}",
    )


_SESSIONS = [
    _make_session("dev", 0, 1, "claude"),
    _make_session("dev", 1, 0, "opencode"),
    _make_session("work", 2, 3, "claude"),
]


@patch("cc_monitor.cli.subprocess.run")
@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_exact_target(
    mock_discover: object,
    mock_run: object,
    monkeypatch: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "dev:0.1"])  # type: ignore[attr-defined]
    main()
    calls = mock_run.call_args_list  # type: ignore[attr-defined]
    assert len(calls) == 2
    assert calls[0].args[0] == ["tmux", "select-window", "-t", "dev:0.1"]
    assert calls[1].args[0] == ["tmux", "select-pane", "-t", "dev:0.1"]


@patch("cc_monitor.cli.subprocess.run")
@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_partial_agent_type(
    mock_discover: object,
    mock_run: object,
    monkeypatch: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "opencode"])  # type: ignore[attr-defined]
    main()
    calls = mock_run.call_args_list  # type: ignore[attr-defined]
    assert len(calls) == 2
    assert calls[0].args[0] == ["tmux", "select-window", "-t", "dev:1.0"]


@patch("cc_monitor.cli.subprocess.run")
@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_partial_session_name(
    mock_discover: object,
    mock_run: object,
    monkeypatch: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "work"])  # type: ignore[attr-defined]
    main()
    calls = mock_run.call_args_list  # type: ignore[attr-defined]
    assert len(calls) == 2
    assert calls[0].args[0] == ["tmux", "select-window", "-t", "work:2.3"]


@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_no_match(
    mock_discover: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "nonexistent"])  # type: ignore[attr-defined]
    try:
        main()
    except SystemExit as e:
        assert e.code == 1
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "No sessions matching" in captured.out


@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_multiple_matches(
    mock_discover: object,
    monkeypatch: object,
    capsys: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "claude"])  # type: ignore[attr-defined]
    try:
        main()
    except SystemExit as e:
        assert e.code == 1
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "Multiple matches" in captured.out


@patch("cc_monitor.cli.subprocess.run")
@patch("cc_monitor.cli.discover_sessions", return_value=_SESSIONS)
def test_attach_case_insensitive(
    mock_discover: object,
    mock_run: object,
    monkeypatch: object,
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "attach", "OPENCODE"])  # type: ignore[attr-defined]
    main()
    calls = mock_run.call_args_list  # type: ignore[attr-defined]
    assert len(calls) == 2
    assert calls[0].args[0] == ["tmux", "select-window", "-t", "dev:1.0"]
