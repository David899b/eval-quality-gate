# eval-quality-gate

**A reproducible, CI-enforced evaluation gate for LLM/RAG systems — across quality, safety, cost, latency and governance.**

[![quality](https://github.com/David899b/eval-quality-gate/actions/workflows/quality.yml/badge.svg)](https://github.com/David899b/eval-quality-gate/actions/workflows/quality.yml)
[![coverage: >=80% branch](https://img.shields.io/badge/coverage-%E2%89%A580%25%20branch-brightgreen)](#testing-principles)
[![python 3.11 | 3.12](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](pyproject.toml)
[![license: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## The problem

Shipping an LLM/RAG feature without an automated gate means every release relies on someone *eyeballing* outputs. The cost of doing nothing is concrete:

- **Silent regressions.** A prompt or model swap improves the average but hides a failure mode nobody asked about. Without a fixed golden set, the regression ships.
- **Single-number theater.** "Accuracy went up" is not a decision. A score with no baseline, no confidence interval and no failure analysis cannot be defended.
- **Unbounded spend and latency.** Nobody notices a token-budget regression or a p95 blow-up until the invoice arrives.
- **Compliance debt.** PII leakage, missing disclaimers and untraceable claims become an audit problem later, at 10x the cost.

`eval-quality-gate` makes quality **checkable, reproducible and enforceable**: one command returns a pass/fail decision with the evidence attached, and CI blocks the merge when the decision is `NO_GO`.

## Quickstart

```bash
python -m eval_quality_gate \
  --golden data/golden_set.json \
  --outputs data/outputs.json \
  --pricing data/pricing.json \
  --report-dir reports
```

No API keys, no network: the reference run is fully deterministic and reproduces on any machine.

Sample run against the bundled golden set:

```
decision=REVIEW  pessimistic=0.705 base=0.823 optimistic=0.940
  - quality: REVIEW (base 0.823 >= 0.70)
  - safety: GO (no forbidden claims or injection echo)
  - cost: GO (total $0.0030 vs budget $0.0500)
  - latency: GO (p95 1388ms vs budget 2000ms)
  - governance: GO (disclaimers present, no PII detected)
report: reports/report.md
report: reports/report.json
```

## Five dimensions, five gates

| Dimension | What it checks | Gate |
|---|---|---|
| **Quality** | semantic score (token-F1 by default, pluggable) + required citations + grounding | confidence band vs thresholds |
| **Safety** | forbidden claims, prompt-injection echo | any hit → `NO_GO` |
| **Cost** | tokens × published price vs a total budget | ≤80% `GO`, ≤100% `REVIEW`, over `NO_GO` |
| **Latency** | p95 of per-call latency vs a budget | ≤80% `GO`, ≤100% `REVIEW`, over `NO_GO` |
| **Governance** | mandatory disclaimers/phrases, PII (email/SSN/card/phone) | any miss → `NO_GO` |

The overall decision is **the worst dimension** — one `NO_GO` anywhere blocks the release. Exit code is `0` for `GO`/`REVIEW` and `1` for `NO_GO`, so it drops straight into CI.

## Three scenarios, always

No single number is reported. Every score is anchored to a measurable baseline and expressed as a **pessimistic / base / optimistic** band (one-sided 95% confidence interval):

- **GO** requires the *pessimistic* bound to clear the GO threshold (defensible even in the bad case).
- **REVIEW** is the middle ground between the review and GO thresholds.
- **NO_GO** is below the review threshold, or any hard check fails.

## Architecture

```
src/eval_quality_gate/
├── models.py      # frozen data contracts (Example, CandidateOutput, Decision, ...)
├── loaders.py     # validate golden set + candidate outputs (stdlib JSON)
├── checks.py      # deterministic checks: schema, forbidden, injection, grounding, PII, disclaimers
├── scorers.py     # pure semantic scorers: (expected, answer) -> [0, 1]
├── cost.py        # token usage × price
├── latency.py     # percentiles without numpy
├── gate.py        # confidence band + per-dimension decisions + worst-case rollup
├── report.py      # Markdown + JSON evidence
└── cli.py         # one command, one exit code
```

Design rule: **only `checks.py` and `scorers.py` look at content; nothing here does I/O or network except the loaders and the report writer.** That keeps the gate pure, fast and trivially testable.

## Testing principles

The interesting part of this repo is not the code — it is how the code is proven to be correct.

- **Behaviour over coverage.** CI enforces a **branch-coverage floor of 80%** (`--cov-fail-under=80`); coverage is a floor, not a goal.
- **Deterministic first, semantic second.** Cheap checks short-circuit expensive scoring.
- **Property-based tests** (Hypothesis) prove invariants: `token_f1` is bounded and symmetric, `exact_match` is reflexive, every generated email is flagged as PII.
- **Known limitations are tests.** See [`tests/test_xfail_limits.py`](tests/test_xfail_limits.py): each documented limitation is a `xfail(strict=True)` test. If a limitation silently disappears, the build *breaks* and a human revisits the scorer and the report.
- **Mutation testing** proves the tests bite (see `scripts/check_mutation_score.py`, ≥70%).
- **Full toolchain in CI:** `ruff` (lint + format), `mypy --strict`, `pytest --cov`, `hypothesis`, `mutmut`, `bandit` (SAST), `pip-audit` (SCA), on Python 3.11 and 3.12.

### Known limitations (encoded as `xfail(strict=True)`)

The default scorer is token overlap, which is deliberately simple and cheap. It **cannot detect negation** (`"service is available"` vs `"service is NOT available"`) and **ignores word order**. Those are shipping limitations, documented and pinned so they cannot silently change. The fix path is to register an embedding-similarity or LLM-as-judge scorer — the registry is designed for it.

## Failure analysis, not just scores

Every element that fails a check is captured in the report with its input and reason (`reports/report.md`, `reports/report.json`). Reviewers see *which* case broke and *why*, not only a number.

## Cost and latency are first-class

Cost is `tokens × price` from `data/pricing.json`; latency is measured per call and gated on **p95**. Both have explicit budgets in the gate policy, so a token-budget or latency regression fails the build the same way a quality regression does.

## Governance

The gate enforces governance *mechanically*: mandatory disclaimers must be present, and no PII may appear in an answer. The evaluation artifacts are audit-ready (decision, thresholds, per-example evidence, provenance of every number). See [`MODEL_CARD.md`](MODEL_CARD.md). Policy ownership stays with legal/risk — this repo produces the **evidence**, not the policy.

## Role fit & competitive landscape

This project is deliberately shaped around what 2026 "AI Evaluation Engineer / Model Evaluation Engineer" roles actually ask for, and around the standard tooling candidates are compared against (`promptfoo`, `DeepEval`, `Inspect AI`, `Ragas`, ...). See:

- [`docs/MARKET-VERDICT.md`](docs/MARKET-VERDICT.md) — what the market demands, with sources.
- [`docs/COMPETENCY-MATRIX.md`](docs/COMPETENCY-MATRIX.md) — how multinationals score this work.
- [`docs/TESTING-PRINCIPLES.md`](docs/TESTING-PRINCIPLES.md) — the principles behind the test design.
- [`docs/QA-TOOLING.md`](docs/QA-TOOLING.md) — the toolchain and why each tool is there.

## Trade-offs and what is intentionally out of scope

- **No live model calls.** The reference run is offline and deterministic on purpose; plug in a real provider behind the same interface for a scored run.
- **Token-F1 default scorer.** Cheap and explainable; not yet a calibrated judge.
- **No production monitoring / drift/online A-B.** That is a platform concern, not a repo. Tracked as future work.
- **Governance is technical only.** No policy authoring; that is a shared function with legal/risk.

## Reproduce locally without installing anything

```bash
python3 scripts/run_stdlib_checks.py   # 18/18 behavioural checks, stdlib only
```

The full toolchain runs in CI.
