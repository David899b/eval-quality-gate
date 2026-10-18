"""Load and validate the golden set and candidate outputs (stdlib only)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from .models import CandidateOutput, Example


def load_golden_set(path: str | Path) -> list[Example]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("golden set must be a non-empty JSON list")
    examples: list[Example] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            raise ValueError(f"example #{index} is not an object")
        for key in ("id", "question", "expected"):
            if not item.get(key):
                raise ValueError(f"example #{index} is missing required field {key!r}")
        example_id = str(item["id"])
        if example_id in seen:
            raise ValueError(f"duplicate example id: {example_id}")
        seen.add(example_id)
        examples.append(
            Example(
                id=example_id,
                question=str(item["question"]),
                context=str(item.get("context", "")),
                expected=str(item["expected"]),
                category=str(item.get("category", "general")),
                forbidden=tuple(str(x) for x in item.get("forbidden", [])),
                required_citations=tuple(str(x) for x in item.get("required_citations", [])),
                required_phrases=tuple(str(x) for x in item.get("required_phrases", [])),
            )
        )
    return examples


def load_outputs(path: str | Path) -> dict[str, CandidateOutput]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("outputs must be a JSON object keyed by example id")
    outputs: dict[str, CandidateOutput] = {}
    for key, value in raw.items():
        if not isinstance(value, Mapping):
            raise ValueError(f"output {key!r} is not an object")
        citations = value.get("citations", [])
        if not isinstance(citations, list):
            raise ValueError(f"output {key!r} 'citations' must be a list")
        outputs[str(key)] = CandidateOutput(
            answer=str(value.get("answer", "")),
            citations=tuple(str(c) for c in citations),
            tokens_in=int(value.get("tokens_in", 0)),
            tokens_out=int(value.get("tokens_out", 0)),
            latency_ms=float(value.get("latency_ms", 0.0)),
        )
    return outputs
