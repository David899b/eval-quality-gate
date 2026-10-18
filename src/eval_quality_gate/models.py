"""Immutable data contracts for the evaluation harness.

Every value object here is frozen: results must be reproducible and safe to
share across threads and report writers.
"""
from __future__ import annotations

from dataclasses import dataclass

DIMENSIONS: tuple[str, ...] = ("quality", "safety", "cost", "latency", "governance")
STATUS_ORDER: dict[str, int] = {"GO": 0, "REVIEW": 1, "NO_GO": 2}


@dataclass(frozen=True)
class Example:
    """One golden-set item: the question, the grounding context and the rubric."""

    id: str
    question: str
    context: str
    expected: str
    category: str = "general"
    forbidden: tuple[str, ...] = ()
    required_citations: tuple[str, ...] = ()
    required_phrases: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateOutput:
    """What the system under test returned for one example."""

    answer: str
    citations: tuple[str, ...] = ()
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0


@dataclass(frozen=True)
class CheckResult:
    name: str
    dimension: str
    passed: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoreResult:
    name: str
    value: float


@dataclass(frozen=True)
class ExampleResult:
    example_id: str
    category: str
    checks: tuple[CheckResult, ...]
    scores: tuple[ScoreResult, ...]
    cost_usd: float
    latency_ms: float
    answer: str

    @property
    def checks_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def semantic_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.value for s in self.scores) / len(self.scores)

    def failed_checks(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if not c.passed)

    def has_failed_dimension(self, dimension: str) -> bool:
        return any(c.dimension == dimension and not c.passed for c in self.checks)


@dataclass(frozen=True)
class Scenario:
    """A pessimistic / base / optimistic confidence band on a score."""

    name: str
    pessimistic: float
    base: float
    optimistic: float


@dataclass(frozen=True)
class GatePolicy:
    """Thresholds that turn measurements into a release decision."""

    go_threshold: float = 0.85
    review_threshold: float = 0.70
    max_p95_latency_ms: float = 2000.0
    max_total_cost_usd: float = 0.05
    require_all_checks: bool = True


@dataclass(frozen=True)
class DimensionResult:
    dimension: str
    status: str
    detail: str


@dataclass(frozen=True)
class Decision:
    status: str
    dimensions: tuple[DimensionResult, ...]
    scenario: Scenario
    policy: GatePolicy
    reasons: tuple[str, ...] = ()

    def dimension(self, name: str) -> DimensionResult | None:
        for d in self.dimensions:
            if d.dimension == name:
                return d
        return None
