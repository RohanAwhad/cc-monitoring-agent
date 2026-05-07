from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
import time
import uuid

from loguru import logger

from cc_monitor.analyzer import analyze_sessions
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


def _run_attach(args: argparse.Namespace) -> None:
    target: str = args.target
    sessions = discover_sessions()

    matches = [s for s in sessions if s.tmux_target == target]
    if not matches:
        lower_target = target.lower()
        matches = [
            s
            for s in sessions
            if lower_target in s.tmux_target.lower()
            or lower_target in s.agent_type.lower()
            or lower_target in s.session_name.lower()
        ]

    if len(matches) == 1:
        t = matches[0].tmux_target
        subprocess.run(["tmux", "select-window", "-t", t])
        subprocess.run(["tmux", "select-pane", "-t", t])
    elif len(matches) > 1:
        print("Multiple matches found:")
        for i, s in enumerate(matches, 1):
            print(f"  {i}. {s.tmux_target} ({s.agent_type})")
        sys.exit(1)
    else:
        print(f"No sessions matching '{target}'")
        sys.exit(1)


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
    status_parser.set_defaults(func=_run_status)

    attach_parser = subparsers.add_parser(
        "attach", help="jump to a specific agent's tmux pane"
    )
    attach_parser.add_argument(
        "target", help="tmux target or partial match (agent type, session name)"
    )
    attach_parser.set_defaults(func=_run_attach)

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
