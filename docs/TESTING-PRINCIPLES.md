# Testing principles applied in this repo

1. **Test behaviour, not coverage.** Coverage is a floor, not a goal.
   Target: overall ≥80% (branch), critical paths 100%. A test that executes a
   line with no assertion adds nothing.
2. **Deterministic first, semantic second.** Cheap, network-free checks run
   before expensive scoring. A hard failure short-circuits the gate.
3. **Isolate the non-deterministic.** Unit tests mock the model and the network;
   integration/“long-running” tests are marked and run separately.
4. **Property-based tests** (Hypothesis) generate thousands of inputs and shrink
   failures to a minimal case.
5. **`xfail(strict=True)` encodes known limitations.** If a documented limitation
   ever stops failing, the build breaks — no silent regressions.
6. **Mutation testing** proves the tests actually detect bugs (not just pass).
7. **Statistical rigour.** Measure run-to-run variance; anchor every number to a
   baseline. Report a pessimistic / base / optimistic band, never one number.
8. **Reproducibility is non-negotiable.** If a reviewer cannot reproduce a result,
   it does not count: fixed seeds, pinned deps, relative paths, one command.
9. **Traceability.** Every result ties back to the run, code and dataset that
   produced it.

## How to run

```bash
# fast path, no network
pytest -m "not integration" --cov --cov-fail-under=80

# full toolchain (matches CI)
ruff check . && ruff format --check . && mypy src
pytest --cov --cov-report=term-missing --cov-fail-under=80
python scripts/check_mutation_score.py --threshold 70
```
