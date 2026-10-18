# Competency matrix — how multinationals score this work, and where this repo lands

Hiring and platform-review rubrics for AI-evaluation work (2026) converge on four
weighted dimensions. This repo is mapped against them so a reviewer can see the
evidence in one place.

| Dimension | Weight | What reviewers look for | Evidence in this repo |
|---|---|---|---|
| **Problem framing & metrics** | 20% | target + thresholds tied to a decision; baselines | `README` "The problem"; gate policy in `gate.py`; 3-scenario band |
| **Modeling & code quality** | 30% | reproducible pipeline, tests, clear interfaces | `src/` boundaries; pytest + hypothesis; mutation gate; ruff/mypy strict |
| **System & production design** | 30% | cost/latency budgets, observability, rollback/failure probes | cost & latency gates; CI artifacts; failure analysis in report |
| **Collaboration & communication** | 20% | exposes uncertainty, documents trade-offs and risk | confidence band, `MODEL_CARD.md`, known-limitations section, guión |

## Required artifacts → where they are

| Artifact | Location |
|---|---|
| Reproducible pipeline (one command) | `README.md` → Quickstart, `cli.py` |
| Model card | [`../MODEL_CARD.md`](../MODEL_CARD.md) |
| Eval harness beyond accuracy | `checks.py` + `scorers.py` + `gate.py` |
| Latency + cost notes | `latency.py`, `cost.py`, budgets in `GatePolicy` |
| Failure analysis | `reports/report.md` (failed input / expected / actual / reason) |
| CI badge + artifacts | `.github/workflows/quality.yml` |
| Known limitations | `tests/test_xfail_limits.py` |

## The rubric, applied

- **Framing (20%):** the README opens with the *cost of not doing nothing*, and
  every threshold is a defendable, editable constant — not a magic number.
- **Code quality (30%):** frozen dataclasses, pure scorers, stdlib core, `mypy
  --strict`, ~80% branch coverage floor, mutation testing, property tests.
- **Production design** | 30% | explicit cost and p95 latency budgets; CI
  artifacts with the failed case; documented rollback path (fix scorer / tighten
  threshold, never "ship and pray").
| **Communication** | 20% | decision is a plain `GO/REVIEW/NO_GO` with the reason; failures are explained, not hidden; limitations are declared up front. |

## Deliberate gaps (honesty is a scored behavior)

- No live model in the reference run (deterministic by design).
- No full OWASP red-team suite, no agentic tool-call eval, no LLM-as-judge
  calibration, no fairness slicing, no production drift monitoring.
  These are named in `README.md` and `EVALUACION_QA.md` as the next suite.
