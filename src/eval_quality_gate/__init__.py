"""eval-quality-gate: a reproducible, CI-enforced evaluation gate.

Public API surface intentionally small and stable.
"""

from .gate import confidence_band, decide, evaluate, scenario_from_results
from .loaders import load_golden_set, load_outputs
from .models import (
    CandidateOutput,
    Decision,
    DimensionResult,
    Example,
    ExampleResult,
    GatePolicy,
    Scenario,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "CandidateOutput",
    "Decision",
    "DimensionResult",
    "Example",
    "ExampleResult",
    "GatePolicy",
    "Scenario",
    "confidence_band",
    "decide",
    "evaluate",
    "load_golden_set",
    "load_outputs",
    "scenario_from_results",
]
