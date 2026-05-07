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
