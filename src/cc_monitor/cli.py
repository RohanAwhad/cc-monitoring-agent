from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
import uuid

from loguru import logger

from cc_monitor.analyzer import analyze_sessions
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import display_results
from cc_monitor.logging import setup_logging
from cc_monitor.models import AgentSession


def _apply_session_filters(
    sessions: list[AgentSession],
    state: str | None,
    agent: str | None,
) -> list[AgentSession]:
    result = sessions
    if state is not None:
        result = [s for s in result if s.state == state]
    if agent is not None:
        result = [s for s in result if s.agent_type == agent]
    return result


def _apply_session_ordering(
    sessions: list[AgentSession],
    key: str,
) -> list[AgentSession]:
    return sorted(sessions, key=lambda s: getattr(s, key))


def _run_status(args: argparse.Namespace) -> None:
    scan_id = uuid.uuid4().hex[:8]
    log = logger.bind(scan_id=scan_id)

    t0 = time.monotonic()
    sessions = discover_sessions()
    log.debug("discovered {} raw sessions", len(sessions))
    sessions = analyze_sessions(sessions)
    elapsed_ms = (time.monotonic() - t0) * 1000
    log.info("found {} sessions ({:.0f}ms)", len(sessions), elapsed_ms)

    sessions = _apply_session_filters(sessions, args.filter_state, args.filter_agent)
    sessions = _apply_session_ordering(sessions, args.sort_key)

    if args.json_output:
        log.debug("outputting JSON results")
        json.dump(
            {"sessions": [dataclasses.asdict(s) for s in sessions]},
            sys.stdout,
            indent=2,
        )
        print()
    else:
        log.debug("displaying table results")
        display_results(sessions)


def _run_watch(args: argparse.Namespace) -> None:
    from cc_monitor.watch import watch_loop

    watch_loop(interval=args.interval)


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="ccm",
        description="Monitor Claude Code and OpenCode agent sessions in tmux",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="output results as JSON",
    )
    parser.set_defaults(filter_state=None, filter_agent=None, sort_key="state")
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="show current session status")
    status_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="output results as JSON",
    )
    status_parser.add_argument(
        "--state",
        choices=["working", "idle", "needs_input"],
        default=None,
        dest="filter_state",
        help="filter sessions by state",
    )
    status_parser.add_argument(
        "--agent",
        choices=["claude", "opencode"],
        default=None,
        dest="filter_agent",
        help="filter sessions by agent type",
    )
    status_parser.add_argument(
        "--sort",
        choices=["state", "agent_type", "tmux_target"],
        default="state",
        dest="sort_key",
        help="sort sessions by field (default: state)",
    )
    status_parser.set_defaults(func=_run_status)

    watch_parser = subparsers.add_parser(
        "watch", help="continuously monitor sessions with live refresh"
    )
    watch_parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="refresh interval in seconds (default: 2)",
    )
    watch_parser.set_defaults(func=_run_watch)

    args = parser.parse_args()

    if args.command is None:
        _run_status(args)
    else:
        args.func(args)
