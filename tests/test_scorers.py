from __future__ import annotations

import pytest

from eval_quality_gate.scorers import DEFAULT_SCORERS, exact_match, score_answer, token_f1


def test_exact_match_identity():
    assert exact_match("hello world", "hello world") == 1.0


def test_exact_match_case_and_space_insensitive():
    assert exact_match("Hello  World ", " hello world") == 1.0


def test_exact_match_different():
    assert exact_match("hello", "bye") == 0.0


def test_token_f1_perfect():
    assert token_f1("a b c", "a b c") == 1.0


def test_token_f1_empty_is_zero():
    assert token_f1("", "a b") == 0.0
    assert token_f1("a b", "") == 0.0


def test_token_f1_partial_between_zero_and_one():
    value = token_f1("the quick brown fox", "the quick fox")
    assert 0.0 < value < 1.0


@pytest.mark.parametrize("gold,pred", [("a", "a"), ("a b", "b a"), ("x", "y")])
def test_token_f1_bounds(gold, pred):
    assert 0.0 <= token_f1(gold, pred) <= 1.0


def test_score_answer_returns_one_per_scorer():
    results = score_answer("a", "a")
    assert len(results) == len(DEFAULT_SCORERS)
    assert {s.name for s in results} == set(DEFAULT_SCORERS)
