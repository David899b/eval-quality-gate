# Market verdict — is a multi-dimension eval gate "in scope" for an AI Evaluation Engineer?

**Verdict: yes, in scope — with one nuance (governance is a shared function).**
This document records the evidence so the decision is not based on opinion.

## 1. The role, from real 2026 postings

| Source (role) | Dimensions named verbatim |
|---|---|
| Wipro — *AI Evaluation Engineer* | harnesses, **benchmarking & reliability**, run-to-run variance, Git/CI/CD |
| Rubrik — *Senior AI Evals Engineer* | **correctness, latency, cost, safety**, red-teaming, bias, toxicity, model selection |
| EY — *Agentic AI Evaluation Engineer* | answer quality, grounding, **agentic behavior**, **operational quality (latency, cost/token budget)**, OWASP LLM Top 10 |
| Deepgram | WER, hallucination, **latency, time-to-first-byte**, CI gates, canaries |
| NVIDIA (AI Safety & Security) | measurement rigor, reproducibility, traceability, run→result mapping |
| neurogent.ai | explicit role: "Eval / QA / **Model Governance / FinOps**" |
| Autodesk / Rubrik / Wipro | governance, Responsible AI, model cards, regulatory compliance |

**Verdict:** cost, latency and safety are **core** to the role. Governance is
**shared** — the eval engineer produces audit-ready evidence, model cards and
traceability; policy ownership sits with legal/risk/policy teams.

## 5. Sources (2026)

- Wipro — AI Evaluation Engineer (careers.wipro.com)
- Rubrik — Senior AI Evals Test Engineer (rubrik.com/careers)
- EY — Agentic AI Evaluation Engineer (careers.ey.com)
- Deepgram — Senior Software Engineer, Evals (simplify.jobs)
- NVIDIA — Evaluation & ML Systems Engineer, AI Safety (nvidia.wd5.myworkdayjobs.com)
- neurogent.ai — Senior AI Platform Engineer, Eval/QA/Governance/FinOps
- Devopsschool — Senior/Lead AI Evaluation Engineer role blueprints
- AI evals tooling surveys (dev.to / tool comparisons, 2026)
