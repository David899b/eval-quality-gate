"""Render machine-readable (JSON) and human-readable (Markdown) evidence."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from .models import Decision, ExampleResult


def to_json(results: Sequence[ExampleResult], decision: Decision) -> dict:
    return {
        "decision": {
            "status": decision.status,
            "scenario": {
                "name": decision.scenario.name,
                "pessimistic": round(decision.scenario.pessimistic, 4),
                "base": round(decision.scenario.base, 4),
                "optimistic": round(decision.scenario.optimistic, 4),
            },
            "dimensions": [
                {"dimension": d.dimension, "status": d.status, "detail": d.detail} for d in decision.dimensions
            ],
            "policy": {
                "go_threshold": decision.policy.go_threshold,
                "review_threshold": decision.policy.review_threshold,
                "max_p95_latency_ms": decision.policy.max_p95_latency_ms,
                "max_total_cost_usd": decision.policy.max_total_cost_usd,
            },
            "reasons": list(decision.reasons),
        },
        "examples": [
            {
                "id": r.example_id,
                "category": r.category,
                "checks": [
                    {"name": c.name, "dimension": c.dimension, "passed": c.passed, "reasons": list(c.reasons)}
                    for c in r.checks
                ],
                "scores": [{"name": s.name, "value": s.value} for s in r.scores],
                "semantic": round(r.semantic_score, 4),
                "cost_usd": round(r.cost_usd, 6),
                "latency_ms": round(r.latency_ms, 1),
            }
            for r in results
        ],
    }


def to_markdown(results: Sequence[ExampleResult], decision: Decision) -> str:
    lines: list[str] = [
        "# Evaluation report",
        "",
        f"**Decision: `{decision.status}`**",
        "",
        "## Dimensions",
        "",
        "| dimension | status | detail |",
        "|---|---|---|",
    ]
    for d in decision.dimensions:
        lines.append(f"| {d.dimension} | {d.status} | {d.detail} |")
    lines += [
        "",
        "## Score band (quality)",
        "",
        "| scenario | score |",
        "|---|---|",
        f"| pessimistic | {decision.scenario.pessimistic:.3f} |",
        f"| base | {decision.scenario.base:.3f} |",
        f"| optimistic | {decision.scenario.optimistic:.3f} |",
        "",
        f"Thresholds: GO >= {decision.policy.go_threshold:.2f} on pessimistic, "
        f"REVIEW >= {decision.policy.review_threshold:.2f} on base.",
        "",
        "## Per-example results",
        "",
        "| id | category | forbidden | injection | citations | grounding | disclaimers | pii | semantic |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    names = ("forbidden_claims", "prompt_injection", "required_citations", "grounding", "required_phrases", "no_pii")
    for r in results:
        mark = {c.name: ("PASS" if c.passed else "**FAIL**") for c in r.checks}
        row = [r.example_id, r.category] + [mark.get(n, "-") for n in names] + [f"{r.semantic_score:.3f}"]
        lines.append("| " + " | ".join(row) + " |")

    failures = [c for r in results for c in r.failed_checks()]
    if failures:
        lines += ["", "## Failures (evidence)", ""]
        for r in results:
            for c in r.failed_checks():
                lines.append(f"- `{r.example_id}` [{c.dimension}/{c.name}]: " + "; ".join(c.reasons))
    else:
        lines += ["", "_All deterministic checks passed._"]

    return "\n".join(lines) + "\n"


def write_reports(report_dir: str | Path, results: Sequence[ExampleResult], decision: Decision) -> tuple[Path, Path]:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    markdown_path = directory / "report.md"
    json_path = directory / "report.json"
    markdown_path.write_text(to_markdown(results, decision), encoding="utf-8")
    json_path.write_text(json.dumps(to_json(results, decision), indent=2), encoding="utf-8")
    return markdown_path, json_path
