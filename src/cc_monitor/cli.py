import argparse
import json
import sys


def main() -> None:
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

    sessions: list[dict[str, str]] = []

    if args.json_output:
        json.dump({"sessions": sessions}, sys.stdout, indent=2)
        print()
    else:
        print("No agent sessions found in tmux.")
