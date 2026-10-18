from __future__ import annotations

from eval_quality_gate.checks import (
    check_citations,
    check_forbidden,
    check_grounding,
    check_pii,
    check_prompt_injection,
    check_required_phrases,
    check_schema,
    run_checks,
)
from eval_quality_gate.models import CandidateOutput


def test_schema_accepts_valid(good_output):
    assert check_schema(good_output).passed


def test_schema_rejects_empty_answer():
    assert not check_schema(CandidateOutput(answer="")).passed


def test_forbidden_detects_phrase(example):
    out = CandidateOutput(answer="This is a guaranteed refund anytime.")
    result = check_forbidden(out, example)
    assert not result.passed
    assert len(result.reasons) == 2


def test_forbidden_passes_when_absent(example, good_output):
    assert check_forbidden(good_output, example).passed


def test_prompt_injection_detects_signature():
    out = CandidateOutput(answer="Sure, I will ignore previous instructions.")
    assert not check_prompt_injection(out).passed


def test_prompt_injection_clean(good_output):
    assert check_prompt_injection(good_output).passed


def test_citations_missing(example):
    out = CandidateOutput(answer="ok", citations=())
    assert not check_citations(out, example).passed


def test_grounding_flags_unknown_citation(example):
    out = CandidateOutput(answer="ok", citations=("policy#invented",))
    assert not check_grounding(out, example).passed


def test_required_phrases_governance(example):
    example = example.__class__(**{**example.__dict__, "required_phrases": ("not legal advice",)})
    out = CandidateOutput(answer="No disclaimer here.")
    assert not check_required_phrases(out, example).passed


def test_pii_detection_flags_email():
    out = CandidateOutput(answer="Contact me at jane.doe@example.com")
    assert not check_pii(out).passed


def test_run_checks_returns_all_dimensions(example, good_output):
    results = run_checks(good_output, example)
    dimensions = {c.dimension for c in results}
    assert {"quality", "safety", "governance"} <= dimensions
    assert all(c.passed for c in results)
