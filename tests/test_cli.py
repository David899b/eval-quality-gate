from __future__ import annotations

import json

from eval_quality_gate.cli import main


def _write_inputs(tmp_path, forbidden_hit: bool = False):
    golden = [
        {
            "id": "e1",
            "question": "q",
            "context": "fact [src#1]",
            "expected": "the answer",
            "forbidden": ["secret"],
            "required_citations": ["src#1"],
        }
    ]
    answer = "the secret" if forbidden_hit else "the answer"
    outputs = {"e1": {"answer": answer, "citations": ["src#1"], "tokens_in": 10, "tokens_out": 5, "latency_ms": 50}}
    pricing = {"price_per_1k_input_usd": 0.001, "price_per_1k_output_usd": 0.002}
    (tmp_path / "golden.json").write_text(json.dumps(golden))
    (tmp_path / "outputs.json").write_text(json.dumps(outputs))
    (tmp_path / "pricing.json").write_text(json.dumps(pricing))
    return tmp_path


def test_cli_passes_and_writes_reports(tmp_path):
    inputs = _write_inputs(tmp_path)
    report_dir = tmp_path / "reports"
    code = main(
        [
            "--golden",
            str(inputs / "golden.json"),
            "--outputs",
            str(inputs / "outputs.json"),
            "--pricing",
            str(inputs / "pricing.json"),
            "--report-dir",
            str(report_dir),
        ]
    )
    assert code == 0
    assert (report_dir / "report.md").exists()
    assert (report_dir / "report.json").exists()


def test_cli_blocks_on_safety_failure(tmp_path):
    inputs = _write_inputs(tmp_path, forbidden_hit=True)
    code = main(
        [
            "--golden",
            str(inputs / "golden.json"),
            "--outputs",
            str(inputs / "outputs.json"),
            "--pricing",
            str(inputs / "pricing.json"),
            "--report-dir",
            str(tmp_path / "reports"),
        ]
    )
    assert code == 1


def test_cli_bad_input_returns_two(tmp_path):
    assert main(["--golden", str(tmp_path / "missing.json"), "--outputs", str(tmp_path / "x.json")]) == 2
