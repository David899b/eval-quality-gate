# Model Card — eval-quality-gate

## Overview

`eval-quality-gate` is an **evaluation harness**, not a model. It measures a
candidate system (a model + prompt + retrieval stack) against a versioned golden
set and produces a release decision across five dimensions.

- **Intended users:** AI evaluation / ML platform engineers, release owners, and
  reviewers who need an auditable pass/fail on AI quality.
- **Intended use:** CI/CD quality gate, pre-release regression testing, model /
  prompt / retrieval comparison, and evidence generation for review.
- **Out of scope:** training, serving, production monitoring, policy authoring.

## What it measures

| Dimension | Measurement | Data provenance |
|---|---|---|
| Quality | token-F1 (default) or a registered scorer, plus citation and grounding checks | golden set + candidate outputs |
| Safety | forbidden-claim and prompt-injection signatures | configurable lexicons |
| Cost | `tokens_in/out × price_per_1k` | `data/pricing.json` |
| Latency | p95 of per-call latency | candidate outputs |
| Governance | required phrases/disclaimers, PII regexes | golden set + answer text |

## Limitations and known risks

- **Token-F1 is surface-level.** It cannot detect negation or word order
  (pinned as `xfail(strict=True)`). Use an embedding or judge scorer for
  meaning-sensitive use cases.
- **Not statistically powered by default.** The bundled golden set is small and
  illustrative; production use requires stratified coverage and minimum sample
  sizes per risk tier.
- **Deterministic reference provider.** The bundled run uses recorded outputs,
  so it does not exercise a live model. Wire a real provider to measure one.
- **Regex-based PII.** Catches common formats (email, SSN, card, phone); it is
  not a compliance-grade DLP. Do not rely on it as the sole control.
- **No adversarial red-team suite bundled.** Prompt-injection coverage is a
  representative signature list, not the full OWASP LLM Top 10.

## Ethical and governance considerations

- The harness emits **evidence**, not policy. Human oversight and the sign-off
  of a policy/legal owner remain required before a release.
- Evaluation data must be de-identified and provenance-documented before it is
  shared; the bundled data is synthetic.
- Thresholds encode risk tolerance and must be agreed with the accountable
  product/risk owner, not set by the harness author alone.

## Metrics reported

Every run reports, per dimension: status (`GO`/`REVIEW`/`NO_GO`), a detail
string, and per-example evidence. Quality is reported as a pessimistic / base /
optimistic confidence band, never a single number.
