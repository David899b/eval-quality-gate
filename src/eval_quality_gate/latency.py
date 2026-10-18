"""Latency statistics. Percentiles without numpy, so the core stays stdlib."""

from __future__ import annotations

import math
from collections.abc import Sequence


def percentile(values: Sequence[float], p: float) -> float:
    """Linear-interpolation percentile (same method as numpy's default)."""
    if not values:
        return 0.0
    xs = sorted(float(v) for v in values)
    if len(xs) == 1:
        return xs[0]
    rank = (len(xs) - 1) * (p / 100.0)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return xs[int(rank)]
    return xs[low] * (high - rank) + xs[high] * (rank - low)


def p95(values: Sequence[float]) -> float:
    return percentile(values, 95.0)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0
