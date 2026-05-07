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
    args = parser.parse_args()

    t0 = time.monotonic()
    sessions = discover_sessions()
    sessions = analyze_sessions(sessions)
    elapsed_ms = (time.monotonic() - t0) * 1000
    logger.info("found {} sessions ({:.0f}ms)", len(sessions), elapsed_ms)

    if args.json_output:
        json.dump(
            {"sessions": [dataclasses.asdict(s) for s in sessions]},
            sys.stdout,
            indent=2,
        )
        print()
    else:
        display_results(sessions)
