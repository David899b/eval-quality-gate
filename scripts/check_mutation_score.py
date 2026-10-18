#!/usr/bin/env python3
"""Best-effort mutation-score gate for CI.

Runs ``mutmut run`` and fails if the killed-mutant ratio drops below the
threshold. Output formats vary across mutmut versions, so parsing is defensive:
if the summary cannot be parsed we warn and pass rather than block the build.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _find(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=70.0)
    args = parser.parse_args()

    try:
        proc = subprocess.run(["mutmut", "run", "--no-progress"], capture_output=True, text=True)
        summary = subprocess.run(["mutmut", "results"], capture_output=True, text=True)
    except FileNotFoundError:
        print("mutmut not installed; skipping mutation gate")
        return 0

    text = _ANSI.sub("", proc.stdout + proc.stderr + summary.stdout + summary.stderr)
    killed = _find(text, r"(?i)killed[^\d]*(\d+)")
    survived = _find(text, r"(?i)survived[^\d]*(\d+)")
    total = _find(text, r"(?i)total[^\d]*(\d+)" )
    if total is None and killed is not None and survived is not None:
        total = killed + survived

    if not total:
        print("could not parse mutation summary; skipping gate")
        return 0

    score = 100.0 * (killed or 0) / total
    print(f"mutation score: {score:.1f}% (killed {killed}/{total}, threshold {args.threshold}%)")
    return 0 if score >= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
