from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
import uuid
from typing import Any

from loguru import logger

from cc_monitor.analyzer import analyze_sessions, estimate_session_cost
from cc_monitor.discovery import discover_sessions
from cc_monitor.display import display_results
from cc_monitor.logging import setup_logging


def _run_status(args: argparse.Namespace) -> None:
    scan_id = uuid.uuid4().hex[:8]
    log = logger.bind(scan_id=scan_id)

    t0 = time.monotonic()
    sessions = discover_sessions()
    log.debug("discovered {} raw sessions", len(sessions))
    sessions = analyze_sessions(sessions)
    elapsed_ms = (time.monotonic() - t0) * 1000
    log.info("found {} sessions ({:.0f}ms)", len(sessions), elapsed_ms)

    show_costs: bool = getattr(args, "costs", False)
    cost_data: dict[str, dict[str, Any] | None] = {}
    if show_costs:
        for s in sessions:
            cost_data[s.tmux_target] = estimate_session_cost(s)

    if args.json_output:
        log.debug("outputting JSON results")
        session_dicts: list[dict[str, object]] = []
        for s in sessions:
            d: dict[str, object] = dataclasses.asdict(s)
            if show_costs:
                d["cost"] = cost_data.get(s.tmux_target)
            session_dicts.append(d)
        json.dump({"sessions": session_dicts}, sys.stdout, indent=2)
        print()
    else:
        log.debug("displaying table results")
        display_results(sessions, cost_data if show_costs else None)


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
    parser.add_argument(
        "--costs",
        action="store_true",
        default=False,
        help="show token usage and estimated cost per session",
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
        "--costs",
        action="store_true",
        default=False,
        help="show token usage and estimated cost per session",
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
