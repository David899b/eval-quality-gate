"""Shared fixtures. No network, no model: everything is deterministic."""

from __future__ import annotations

import pytest

from eval_quality_gate.models import CandidateOutput, Example


@pytest.fixture
def example() -> Example:
    return Example(
        id="refund-window",
        question="How long to request a refund?",
        context="Refunds are available within 30 days [policy#refunds].",
        expected="Customers may request a refund within 30 days.",
        category="policy",
        forbidden=("guaranteed refund", "anytime"),
        required_citations=("policy#refunds",),
    )


@pytest.fixture
def good_output() -> CandidateOutput:
    return CandidateOutput(
        answer="Customers may request a refund within 30 days.",
        citations=("policy#refunds",),
        tokens_in=100,
        tokens_out=20,
        latency_ms=100.0,
    )
