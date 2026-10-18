"""Cost model: token usage x published price. Pure arithmetic, no I/O."""
from __future__ import annotations

import json
from pathlib import Path

from .models import CandidateOutput


def load_pricing(path: str | Path) -> tuple[float, float]:
    """Return (price_per_1k_input_usd, price_per_1k_output_usd)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return (
        float(raw["price_per_1k_input_usd"]),
        float(raw["price_per_1k_output_usd"]),
    )


def compute_cost(output: CandidateOutput, price_in: float, price_out: float) -> float:
    """Cost of a single call, in USD."""
    return (output.tokens_in / 1000.0) * price_in + (output.tokens_out / 1000.0) * price_out


def total_cost(costs: list[float]) -> float:
    return sum(costs)
