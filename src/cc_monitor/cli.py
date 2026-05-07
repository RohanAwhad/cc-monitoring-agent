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
from cc_monitor.display import display_results, format_summary
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


def _run_summary(args: argparse.Namespace) -> None:
    logger.debug("summary subcommand invoked")
    sessions = discover_sessions()
    sessions = analyze_sessions(sessions)
    logger.debug("summary: {} sessions discovered", len(sessions))
    print(format_summary(sessions), end="")


def _run_watch(args: argparse.Namespace) -> None:
    logger.debug("watch subcommand invoked with interval={}", args.interval)
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
    status_parser.set_defaults(func=_run_status)

    summary_parser = subparsers.add_parser(
        "summary", help="one-line summary for tmux status bar"
    )
    summary_parser.set_defaults(func=_run_summary)

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
    logger.debug("parsed command={}", args.command)

    if args.command is None:
        _run_status(args)
    else:
        args.func(args)
