from __future__ import annotations

import json

import pytest

from eval_quality_gate.loaders import load_golden_set, load_outputs


def test_load_valid_golden_set(tmp_path):
    path = tmp_path / "g.json"
    path.write_text(json.dumps([{"id": "a", "question": "q", "expected": "e"}]))
    examples = load_golden_set(path)
    assert len(examples) == 1
    assert examples[0].id == "a"


def test_duplicate_id_raises(tmp_path):
    path = tmp_path / "g.json"
    path.write_text(json.dumps([{"id": "a", "question": "q", "expected": "e"}, {"id": "a", "question": "q", "expected": "e"}]))
    with pytest.raises(ValueError):
        load_golden_set(path)


def test_missing_field_raises(tmp_path):
    path = tmp_path / "g.json"
    path.write_text(json.dumps([{"id": "a", "question": "q"}]))
    with pytest.raises(ValueError):
        load_golden_set(path)


def test_empty_golden_set_raises(tmp_path):
    path = tmp_path / "g.json"
    path.write_text("[]")
    with pytest.raises(ValueError):
        load_golden_set(path)


def test_load_outputs_defaults(tmp_path):
    path = tmp_path / "o.json"
    path.write_text(json.dumps({"a": {"answer": "hi", "citations": ["c"]}}))
    outputs = load_outputs(path)
    assert outputs["a"].answer == "hi"
    assert outputs["a"].tokens_in == 0


def test_load_outputs_rejects_non_list_citations(tmp_path):
    path = tmp_path / "o.json"
    path.write_text(json.dumps({"a": {"answer": "hi", "citations": "nope"}}))
    with pytest.raises(ValueError):
        load_outputs(path)
