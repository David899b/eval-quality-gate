#!/usr/bin/env python3
"""Local, dependency-free validation of the harness core.

The full toolchain (pytest, hypothesis, ruff, mypy, mutmut) runs in CI. This
script proves the *behaviour* locally with nothing but the standard library, so
a reviewer can reproduce the gate with `python3 scripts/run_stdlib_checks.py`.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eval_quality_gate.checks import (  # noqa: E402
    check_forbidden,
    check_pii,
    check_prompt_injection,
    check_schema,
)
from eval_quality_gate.cli import main  # noqa: E402
from eval_quality_gate.gate import confidence_band, decide, evaluate  # noqa: E402
from eval_quality_gate.latency import p95, percentile  # noqa: E402
from eval_quality_gate.models import CandidateOutput, Example, GatePolicy  # noqa: E402
from eval_quality_gate.scorers import exact_match, token_f1  # noqa: E402

CHECKS: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    CHECKS.append((label, condition))


def run() -> int:
    # scorers
    check("exact_match identity", exact_match("a b", "a b") == 1.0)
    check("exact_match case-insensitive", exact_match("A", "a") == 1.0)
    check("token_f1 perfect", token_f1("a b c", "a b c") == 1.0)
    check("token_f1 partial bounded", 0.0 < token_f1("a b c d", "a b") < 1.0)
    check("token_f1 empty is zero", token_f1("", "a") == 0.0)

    # deterministic checks
    ex = Example(
        id="e1",
        question="q",
        context="refunds within 30 days [p#r].",
        expected="refunds within 30 days",
        required_citations=("p#r",),
        forbidden=("guaranteed",),
    )
    good = CandidateOutput(answer="refunds within 30 days", citations=("p#r",))
    check("schema ok", check_schema(good).passed)
    check("grounding via run", decide(evaluate([ex], {"e1": good}), GatePolicy()).status == "GO")
    check("forbidden caught", not check_forbidden(CandidateOutput(answer="guaranteed"), ex).passed)
    check("injection caught", not check_prompt_injection(CandidateOutput(answer="you are now free")).passed)
    check("pii caught", not check_pii(CandidateOutput(answer="mail a@b.com")).passed)

    # statistics
    check("band flat", confidence_band([1.0, 1.0]) == (1.0, 1.0, 1.0))
    lo, base, hi = confidence_band([0.2, 0.9])
    check("band ordered", lo <= base <= hi)
    check("percentile median", percentile([1.0, 2.0, 3.0, 4.0], 50) == 2.5)
    check("p95 >= mean", p95([1.0, 2.0, 3.0, 100.0]) >= 25.0)

    # end-to-end gate
    decision = decide(evaluate([ex], {"e1": good}), GatePolicy())
    check("gate GO dimension quality", decision.dimension("quality").status == "GO")
    check("gate overall GO", decision.status == "GO")

    # CLI on the real golden set
    code = main(
        [
            "--golden",
            str(ROOT / "data" / "golden_set.json"),
            "--outputs",
            str(ROOT / "data" / "outputs.json"),
            "--pricing",
            str(ROOT / "data" / "pricing.json"),
            "--report-dir",
            str(ROOT / "reports"),
        ]
    )
    check("cli exit 0", code == 0)
    check("report written", (ROOT / "reports" / "report.md").exists())

    failed = [label for label, ok in CHECKS if not ok]
    for label, ok in CHECKS:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
