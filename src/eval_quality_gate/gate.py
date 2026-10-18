"""Turn raw measurements into a per-dimension release decision.

Five independent dimensions (quality, safety, cost, latency, governance) are
evaluated separately and combined with a worst-case rule: a single NO_GO
anywhere blocks the release.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from .checks import run_checks
from .cost import compute_cost
from .latency import p95
from .models import (
    STATUS_ORDER,
    CandidateOutput,
    Decision,
    DimensionResult,
    Example,
    ExampleResult,
    GatePolicy,
    Scenario,
)
from .scorers import DEFAULT_SCORERS, Scorer, score_answer


def evaluate_example(
    output: CandidateOutput,
    example: Example,
    price_in: float = 0.0,
    price_out: float = 0.0,
    scorers: dict[str, "Scorer"] | None = None,
) -> ExampleResult:
    checks = run_checks(output, example)
    scores = score_answer(example.expected, output.answer, scorers or DEFAULT_SCORERS)
    return ExampleResult(
        example_id=example.id,
        category=example.category,
        checks=checks,
        scores=scores,
        cost_usd=compute_cost(output, price_in, price_out),
        latency_ms=float(output.latency_ms),
        answer=output.answer,
    )


def evaluate(
    examples: Sequence[Example],
    outputs: Mapping[str, CandidateOutput],
    price_in: float = 0.0,
    price_out: float = 0.0,
    scorers: dict[str, "Scorer"] | None = None,
) -> list[ExampleResult]:
    return [evaluate_example(outputs[e.id], e, price_in, price_out, scorers) for e in examples]


def confidence_band(values: Sequence[float], z: float = 1.96) -> tuple[float, float, float]:
    """One-sided 95% confidence band (pessimistic, base, optimistic).

    Anchors every score to a measurable baseline instead of a single number.
    """
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0.0
    mean = sum(values) / n
    if n < 2:
        return mean, mean, mean
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    stderr = math.sqrt(var / n) if (var := variance) >= 0 else 0.0
    se = math.sqrt(var / n)
    pessimistic = max(0.0, mean - z * se)
    optimistic = min(1.0, mean + z * se)
    return pessimistic, mean, optimistic


def scenario_from_results(results: Sequence[ExampleResult], name: str = "candidate") -> Scenario:
    low, base, high = confidence_band([r.semantic_score for r in results])
    return Scenario(name, low, base, high)


def _quality_dimension(results: Sequence[ExampleResult], policy: GatePolicy) -> DimensionResult:
    if any(r.has_failed_dimension("quality") for r in results):
        return DimensionResult("quality", "NO_GO", "one or more quality checks failed")
    scenario = scenario_from_results(results)
    if scenario.pessimistic >= policy.go_threshold:
        return DimensionResult("quality", "GO", f"pessimistic {scenario.pessimistic:.3f} >= {policy.go_threshold:.2f}")
    if scenario.base >= policy.review_threshold:
        return DimensionResult("quality", "REVIEW", f"base {scenario.base:.3f} >= {policy.review_threshold:.2f}")
    return DimensionResult("quality", "NO_GO", f"base {scenario.base:.3f} < {policy.review_threshold:.2f}")


def _safety(results: Sequence[ExampleResult]) -> DimensionResult:
    failures = [r for r in results if r.has_failed_dimension("safety")]
    if failures:
        return DimensionResult("safety", "NO_GO", f"{len(failures)} example(s) failed safety checks")
    return DimensionResult("safety", "GO", "no forbidden claims or injection echo")


def _governance(results: Sequence[ExampleResult]) -> DimensionResult:
    failures = [r for r in results if r.has_failed_dimension("governance")]
    if failures:
        return DimensionResult("governance", "NO_GO", f"{len(failures)} example(s) failed governance checks")
    return DimensionResult("governance", "GO", "disclaimers present, no PII detected")


def _budget_status(measured: float, budget: float) -> str:
    if budget <= 0:
        return "NO_GO"
    ratio = measured / budget
    if ratio <= 0.8:
        return "GO"
    if ratio <= 1.0:
        return "REVIEW"
    return "NO_GO"


def _cost(results: Sequence[ExampleResult], policy: GatePolicy) -> DimensionResult:
    total = sum(r.cost_usd for r in results)
    status = _budget_status(total, policy.max_total_cost_usd)
    return DimensionResult("cost", status, f"total ${total:.4f} vs budget ${policy.max_total_cost_usd:.4f}")


def _latency(results: Sequence[ExampleResult], policy: GatePolicy) -> DimensionResult:
    measured = p95([r.latency_ms for r in results])
    status = _budget_status(measured, policy.max_p95_latency_ms)
    return DimensionResult("latency", status, f"p95 {measured:.0f}ms vs budget {policy.max_p95_latency_ms:.0f}ms")


def decide(results: Sequence[ExampleResult], policy: GatePolicy | None = None) -> Decision:
    policy = policy or GatePolicy()
    scenario = scenario_from_results(results)
    dimensions = (
        _quality_dimension(results, policy),
        _safety(results),
        _cost(results, policy),
        _latency(results, policy),
        _governance(results),
    )
    worst = max(dimensions, key=lambda d: STATUS_ORDER[d.status])
    status = worst.status
    reasons: list[str] = []
    if status != "GO":
        reasons = [f"{d.dimension}: {d.detail}" for d in dimensions if d.status == status]
    return Decision(status, dimensions, scenario, policy, tuple(reasons))
