"""Command-line entry point: run the gate, write a report, set the exit code.

Exit codes: 0 = GO/REVIEW, 1 = NO_GO (block the merge), 2 = bad input.
"""

from __future__ import annotations

import argparse
import sys

from .cost import load_pricing
from .gate import decide, evaluate
from .loaders import load_golden_set, load_outputs
from .models import GatePolicy
from .report import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eval-quality-gate",
        description="Score a candidate system against a golden set and gate the build.",
    )
    parser.add_argument("--golden", default="data/golden_set.json", help="golden set JSON")
    parser.add_argument("--outputs", default="data/outputs.json", help="candidate outputs JSON")
    parser.add_argument("--pricing", default="data/pricing.json", help="pricing JSON")
    parser.add_argument("--report-dir", default="reports", help="where to write report.{md,json}")
    parser.add_argument("--go", type=float, default=0.85, help="GO threshold on the pessimistic score")
    parser.add_argument("--review", type=float, default=0.70, help="REVIEW threshold on the base score")
    parser.add_argument("--max-cost", type=float, default=0.05, help="total cost budget (USD)")
    parser.add_argument("--max-p95-latency", type=float, default=2000.0, help="p95 latency budget (ms)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        examples = load_golden_set(args.golden)
        outputs = load_outputs(args.outputs)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    missing = [e.id for e in examples if e.id not in outputs]
    if missing:
        print(f"error: missing outputs for ids: {', '.join(missing)}", file=sys.stderr)
        return 2

    price_in, price_out = load_pricing(args.pricing)
    results = evaluate(examples, outputs, price_in, price_out)
    policy = GatePolicy(
        go_threshold=args.go,
        review_threshold=args.review,
        max_total_cost_usd=args.max_cost,
        max_p95_latency_ms=args.max_p95_latency,
    )
    decision = decide(results, policy)
    markdown_path, json_path = write_reports(args.report_dir, results, decision)

    print(
        f"decision={decision.status}  "
        f"pessimistic={decision.scenario.pessimistic:.3f} "
        f"base={decision.scenario.base:.3f} "
        f"optimistic={decision.scenario.optimistic:.3f}"
    )
    for dimension in decision.dimensions:
        print(f"  - {dimension.dimension}: {dimension.status} ({dimension.detail})")
    print(f"report: {markdown_path}")
    print(f"report: {json_path}")
    return 0 if decision.status != "NO_GO" else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
