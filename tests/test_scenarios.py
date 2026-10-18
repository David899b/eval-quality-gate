from __future__ import annotations

import pytest

from eval_quality_gate.gate import confidence_band
from eval_quality_gate.latency import mean, p95, percentile


def test_band_zero_variance_is_flat():
    assert confidence_band([1.0, 1.0, 1.0]) == (1.0, 1.0, 1.0)


def test_band_is_ordered_and_bounded():
    low, base, high = confidence_band([0.2, 0.5, 0.9, 0.4])
    assert 0.0 <= low <= base <= high <= 1.0


def test_band_empty():
    assert confidence_band([]) == (0.0, 0.0, 0.0)


def test_band_single_value():
    assert confidence_band([0.7]) == (0.7, 0.7, 0.7)


@pytest.mark.parametrize("p,expected", [(0.0, 1.0), (50.0, 2.5), (100.0, 4.0)])
def test_percentile_known_values(p, expected):
    assert percentile([1.0, 2.0, 3.0, 4.0], p) == pytest.approx(expected)


def test_p95_ge_mean():
    values = [100.0, 120.0, 150.0, 900.0, 200.0]
    assert p95(values) >= mean(values)


def test_percentile_empty():
    assert percentile([], 95.0) == 0.0
