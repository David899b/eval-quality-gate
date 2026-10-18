"""Property-based tests (Hypothesis). Run in CI where hypothesis is installed."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from eval_quality_gate.checks import check_pii, check_prompt_injection
from eval_quality_gate.models import CandidateOutput
from eval_quality_gate.scorers import exact_match, token_f1


@given(st.text(), st.text())
def test_token_f1_is_bounded(gold: str, pred: str) -> None:
    assert 0.0 <= token_f1(gold, pred) <= 1.0


@given(st.text(), st.text())
def test_token_f1_is_symmetric(a: str, b: str) -> None:
    assert token_f1(a, b) == pytest.approx(token_f1(b, a))


@given(st.text())
def test_exact_match_is_reflexive(text: str) -> None:
    assert exact_match(text, text) == 1.0


@given(st.text(), st.text())
def test_exact_match_is_symmetric(a: str, b: str) -> None:
    assert exact_match(a, b) == exact_match(b, a)


@given(st.emails())
def test_pii_always_flags_email(email: str) -> None:
    assert not check_pii(CandidateOutput(answer=f"reach me at {email}")).passed


@given(st.sampled_from(["ignore previous", "you are now", "disregard the above"]))
def test_injection_signatures_are_flagged(signature: str) -> None:
    assert not check_prompt_injection(CandidateOutput(answer=signature)).passed
