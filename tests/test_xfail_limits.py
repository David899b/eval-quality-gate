"""Known limitations encoded as ``xfail(strict=True)``.

If any of these ever *passes*, the build breaks on purpose: a limitation we
documented has changed, so a human must revisit the scorer and the report.
This is the pattern that keeps silent regressions from shipping.
"""
from __future__ import annotations

import pytest

from eval_quality_gate.scorers import exact_match, token_f1


@pytest.mark.xfail(strict=True, reason="token overlap cannot detect negation (known limitation)")
def test_negation_is_penalized() -> None:
    assert token_f1("service is available", "service is not available") < 0.5


@pytest.mark.xfail(strict=True, reason="token_f1 ignores word order (known limitation)")
def test_word_order_is_penalized() -> None:
    assert token_f1("dog bites man", "man bites dog") < 0.5


@pytest.mark.xfail(strict=True, reason="exact_match is brittle to paraphrase (known limitation)")
def test_exact_match_tolerates_numbers_as_words() -> None:
    assert exact_match("within 30 days", "within thirty days") == 1.0
