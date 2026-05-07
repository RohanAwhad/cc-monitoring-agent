"""Eval scoring script for cc-monitoring-agent.

Runs each eval dimension and outputs a JSON score report.
"""

import json
import subprocess
import sys
from pathlib import Path


def load_profile() -> dict:
    profile_path = Path(__file__).parent.parent / ".factory" / "eval_profile.json"
    with open(profile_path) as f:
        return json.load(f)


def run_dimension(dim: dict) -> dict:
    try:
        result = subprocess.run(
            dim["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent.parent,
        )
        passed = result.returncode == 0
    except subprocess.TimeoutExpired:
        passed = False
        result = None

    return {
        "name": dim["name"],
        "weight": dim["weight"],
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "stdout": (result.stdout[-500:] if result else ""),
        "stderr": (result.stderr[-500:] if result else "timeout"),
    }


def main() -> None:
    profile = load_profile()
    results = [run_dimension(dim) for dim in profile["dimensions"]]

    weighted_score = sum(r["score"] * r["weight"] for r in results)
    total_weight = sum(r["weight"] for r in results)
    final_score = weighted_score / total_weight if total_weight > 0 else 0.0

    report = {
        "score": round(final_score, 4),
        "dimensions": results,
    }

    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
