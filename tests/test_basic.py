from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

from cc_monitor.analyzer import (
    _cwd_to_project_dir_name,
    _find_conversation_files,
    _model_to_tier,
    estimate_session_cost,
)
from cc_monitor.cli import main
from cc_monitor.display import _format_tokens
from cc_monitor.models import AgentSession


def _make_session(cwd: str = "") -> AgentSession:
    return AgentSession(
        session_name="test",
        window_index=0,
        pane_index=0,
        agent_type="claude",
        state="idle",
        summary="",
        pane_pid=1234,
        tmux_target="test:0.0",
        cwd=cwd,
    )


def _make_jsonl_entry(
    input_tokens: int = 100,
    output_tokens: int = 50,
    cache_creation: int = 0,
    cache_read: int = 0,
    model: str = "claude-sonnet-4-6",
) -> str:
    entry = {
        "type": "assistant",
        "sessionId": "abc123",
        "message": {
            "model": model,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_creation_input_tokens": cache_creation,
                "cache_read_input_tokens": cache_read,
            },
        },
    }
    return json.dumps(entry)


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


# --- Cost estimation tests ---


def test_estimate_session_cost_no_cwd() -> None:
    session = _make_session(cwd="")
    result = estimate_session_cost(session)
    assert result is None


def test_estimate_session_cost_no_conversation_files(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "projects").mkdir()
    session = _make_session(cwd="/some/project")
    result = estimate_session_cost(session, claude_dir=claude_dir)
    assert result is None


def test_estimate_session_cost_with_data(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    project_dir = claude_dir / "projects" / "-Users-test-myproject"
    project_dir.mkdir(parents=True)

    jsonl_content = "\n".join(
        [
            _make_jsonl_entry(
                input_tokens=1000, output_tokens=500, model="claude-sonnet-4-6"
            ),
            _make_jsonl_entry(
                input_tokens=2000, output_tokens=1000, model="claude-sonnet-4-6"
            ),
        ]
    )
    (project_dir / "conv1.jsonl").write_text(jsonl_content)

    session = _make_session(cwd="/Users/test/myproject")
    result = estimate_session_cost(session, claude_dir=claude_dir)
    assert result is not None
    assert result["input_tokens"] == 3000
    assert result["output_tokens"] == 1500


def test_estimate_session_cost_accuracy(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    project_dir = claude_dir / "projects" / "-Users-test-proj"
    project_dir.mkdir(parents=True)

    # Sonnet: $3/$15 per MTok
    jsonl_content = _make_jsonl_entry(
        input_tokens=1_000_000, output_tokens=1_000_000, model="claude-sonnet-4-6"
    )
    (project_dir / "conv.jsonl").write_text(jsonl_content)

    session = _make_session(cwd="/Users/test/proj")
    result = estimate_session_cost(session, claude_dir=claude_dir)
    assert result is not None
    # 1M input * $3/MTok + 1M output * $15/MTok = $18
    assert result["estimated_cost_usd"] == 18.0


def test_estimate_session_cost_opus_pricing(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    project_dir = claude_dir / "projects" / "-Users-test-proj2"
    project_dir.mkdir(parents=True)

    # Opus: $15/$75 per MTok
    jsonl_content = _make_jsonl_entry(
        input_tokens=1_000_000, output_tokens=1_000_000, model="claude-opus-4-6"
    )
    (project_dir / "conv.jsonl").write_text(jsonl_content)

    session = _make_session(cwd="/Users/test/proj2")
    result = estimate_session_cost(session, claude_dir=claude_dir)
    assert result is not None
    # 1M input * $15/MTok + 1M output * $75/MTok = $90
    assert result["estimated_cost_usd"] == 90.0


def test_estimate_session_cost_with_cache_tokens(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    project_dir = claude_dir / "projects" / "-Users-test-cached"
    project_dir.mkdir(parents=True)

    jsonl_content = _make_jsonl_entry(
        input_tokens=0,
        output_tokens=0,
        cache_creation=1_000_000,
        cache_read=1_000_000,
        model="claude-sonnet-4-6",
    )
    (project_dir / "conv.jsonl").write_text(jsonl_content)

    session = _make_session(cwd="/Users/test/cached")
    result = estimate_session_cost(session, claude_dir=claude_dir)
    assert result is not None
    assert result["cache_creation_tokens"] == 1_000_000
    assert result["cache_read_tokens"] == 1_000_000
    # cache_write: $3 * 1.25 = $3.75/MTok, cache_read: $3 * 0.1 = $0.30/MTok
    # 1M * $3.75 + 1M * $0.30 = $4.05
    assert result["estimated_cost_usd"] == 4.05


def test_cwd_to_project_dir_name() -> None:
    assert _cwd_to_project_dir_name("/Users/test/project") == "-Users-test-project"
    assert _cwd_to_project_dir_name("/a/b/c") == "-a-b-c"


def test_model_to_tier() -> None:
    assert _model_to_tier("claude-sonnet-4-6") == "sonnet"
    assert _model_to_tier("claude-opus-4-6") == "opus"
    assert _model_to_tier("claude-haiku-4-5") == "haiku"
    assert _model_to_tier("unknown-model") == "sonnet"


def test_format_tokens() -> None:
    assert _format_tokens(500) == "500"
    assert _format_tokens(1500) == "1.5K"
    assert _format_tokens(1_500_000) == "1.5M"


def test_find_conversation_files_missing_projects_dir(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    result = _find_conversation_files("/some/path", claude_dir=claude_dir)
    assert result == []


@patch("cc_monitor.discovery.list_all_panes", return_value=[])
def test_cli_costs_flag_no_sessions(
    mock_panes: object, monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setattr(sys, "argv", ["ccm", "status", "--costs", "--json"])  # type: ignore[attr-defined]
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    data = json.loads(captured.out)
    assert "sessions" in data
