"""Pure semantic scorers: ``(expected, answer) -> [0, 1]``.

No network, no I/O, no global state. That is deliberate: pure scorers are the
easiest thing to unit-test, property-test and mutate. The registry lets us add
scorers (BLEU, embedding similarity, LLM judge) without touching the gate.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable

from .models import ScoreResult

Scorer = Callable[[str, str], float]

_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def exact_match(expected: str, answer: str) -> float:
    """1.0 only when the normalised strings are identical."""
    return 1.0 if expected.strip().lower() == answer.strip().lower() else 0.0


def token_f1(expected: str, answer: str) -> float:
    """Token-overlap F1 (SQuAD style) over lowercased alphanumeric tokens."""
    gold = _tokenize(expected)
    pred = _tokenize(answer)
    if not gold or not pred:
        return 0.0
    overlap = sum((Counter(gold) & Counter(pred)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred)
    recall = overlap / len(gold)
    return 2 * precision * recall / (precision + recall)


# Graded semantic metric(s) used for the confidence band. ``exact_match`` is a
# hard metric, so it is offered as a utility but kept out of the default mean.
DEFAULT_SCORERS: dict[str, Scorer] = {
    "token_f1": token_f1,
}

AVAILABLE_SCORERS: dict[str, Scorer] = {
    "exact_match": exact_match,
    "token_f1": token_f1,
}


def score_answer(expected: str, answer: str, scorers: dict[str, Scorer] | None = None) -> tuple[ScoreResult, ...]:
    """Return one ScoreResult per scorer, rounded for stable reporting."""
    active = scorers or DEFAULT_SCORERS
    return tuple(ScoreResult(name, round(float(fn(expected, answer)), 6)) for name, fn in active.items())
