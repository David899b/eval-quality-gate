from __future__ import annotations

from eval_quality_gate.gate import decide, evaluate
from eval_quality_gate.models import CandidateOutput, Example, GatePolicy

EX = Example(
    id="e1",
    question="q",
    context="fact [src#1].",
    expected="The answer is forty two.",
    required_citations=("src#1",),
)


def _output(answer: str, citations=("src#1",), latency=100.0) -> CandidateOutput:
    return CandidateOutput(answer=answer, citations=citations, tokens_in=10, tokens_out=5, latency_ms=latency)


def test_go_when_perfect_and_within_budget():
    results = evaluate([EX], {"e1": _output("The answer is forty two.")})
    decision = decide(results, GatePolicy())
    assert decision.status == "GO"
    assert decision.dimension("quality").status == "GO"
    assert decision.dimension("safety").status == "GO"


def test_no_go_when_forbidden_present():
    ex = Example(id="e1", question="q", context="c", expected="x", forbidden=("secret",))
    results = evaluate([ex], {"e1": _output("the secret plan is out")})
    decision = decide(results, GatePolicy())
    assert decision.status == "NO_GO"
    assert decision.dimension("safety").status == "NO_GO"


def test_no_go_when_governance_disclaimer_missing():
    ex = Example(id="e1", question="q", context="c", expected="x", required_phrases=("not legal advice",))
    results = evaluate([ex], {"e1": _output("no disclaimer")})
    decision = decide(results, GatePolicy())
    assert decision.dimension("governance").status == "NO_GO"


def test_review_when_quality_between_thresholds():
    # partial overlap -> mid semantic score, all checks pass
    ex = Example(id="e1", question="q", context="c", expected="alpha beta gamma delta")
    results = evaluate([ex], {"e1": _output("alpha beta", citations=())})
    decision = decide(results, GatePolicy(go_threshold=0.9, review_threshold=0.3))
    assert decision.dimension("quality").status == "REVIEW"


def test_cost_budget_exceeded_is_no_go():
    ex = Example(id="e1", question="q", context="c", expected="x")
    out = CandidateOutput(answer="x", citations=(), tokens_in=1_000_000, tokens_out=1_000_000)
    results = evaluate([ex], {"e1": out}, price_in=1.0, price_out=1.0)
    decision = decide(results, GatePolicy(max_total_cost_usd=0.01))
    assert decision.dimension("cost").status == "NO_GO"


def test_latency_budget_exceeded_is_no_go():
    ex = Example(id="e1", question="q", context="c", expected="x")
    results = evaluate([ex], {"e1": _output("x", latency=99999.0)})
    decision = decide(results, GatePolicy(max_p95_latency_ms=1000.0))
    assert decision.dimension("latency").status == "NO_GO"


def test_overall_is_worst_dimension():
    ex = Example(id="e1", question="q", context="c", expected="x", forbidden=("bad",))
    results = evaluate([ex], {"e1": _output("bad")})
    decision = decide(results, GatePolicy())
    assert decision.status == "NO_GO"
