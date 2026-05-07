from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time

from loguru import logger

from cc_monitor.analyzer import analyze_sessions
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import display_results
from cc_monitor.logging import setup_logging
from cc_monitor.models import AgentSession


def filter_sessions(
    sessions: list[AgentSession],
    *,
    state: str | None = None,
    agent: str | None = None,
) -> list[AgentSession]:
    result = sessions
    if state is not None:
        result = [s for s in result if s.state == state]
    if agent is not None:
        result = [s for s in result if s.agent_type == agent]
    return result


def sort_sessions(
    sessions: list[AgentSession],
    key: str | None = None,
) -> list[AgentSession]:
    if key is None:
        return sessions
    if key == "state":
        return sorted(sessions, key=lambda s: s.state)
    if key == "agent":
        return sorted(sessions, key=lambda s: s.agent_type)
    if key == "session":
        return sorted(sessions, key=lambda s: s.session_name)
    return sessions


def _run_status(args: argparse.Namespace) -> None:
    t0 = time.monotonic()
    sessions = discover_sessions()
    sessions = analyze_sessions(sessions)
    elapsed_ms = (time.monotonic() - t0) * 1000
    logger.info("found {} sessions ({:.0f}ms)", len(sessions), elapsed_ms)

    state_filter = getattr(args, "state_filter", None)
    agent_filter = getattr(args, "agent_filter", None)
    sort_key = getattr(args, "sort_key", None)

    sessions = filter_sessions(sessions, state=state_filter, agent=agent_filter)
    sessions = sort_sessions(sessions, key=sort_key)

    if args.json_output:
        json.dump(
            {"sessions": [dataclasses.asdict(s) for s in sessions]},
            sys.stdout,
            indent=2,
        )
        print()
    else:
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
        dest="state_filter",
        help="filter sessions by state",
    )
    status_parser.add_argument(
        "--agent",
        choices=["claude", "opencode"],
        dest="agent_filter",
        help="filter sessions by agent type",
    )
    status_parser.add_argument(
        "--sort",
        choices=["state", "agent", "session"],
        dest="sort_key",
        help="sort output rows by field",
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
