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


def main() -> None:
    setup_logging()

    scan_id = uuid.uuid4().hex[:8]
    log = logger.bind(scan_id=scan_id)

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
    log.debug("parsed args: json_output={}", args.json_output)

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
