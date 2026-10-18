# QA tooling — what, why, and where it runs

| Stage | Tool | Why | Config |
|---|---|---|---|
| Lint | **ruff** | one fast linter replaces flake8/isort/pyupgrade | `[tool.ruff]` |
| Format | **ruff format** | deterministic formatting | `--check` in CI |
| Types | **mypy --strict** | catch interface and `Any` leakage | `[tool.mypy]` |
| Unit tests | **pytest** | the standard; marks to split fast/slow | `[tool.pytest.ini_options]` |
| Coverage | **pytest-cov** | branch coverage, 80% floor | `[tool.coverage.*]` |
| Property tests | **hypothesis** | edge cases example-based tests miss | `tests/test_properties.py` |
| Mutation | **mutmut** | prove the tests bite (≥70%) | `scripts/check_mutation_score.py` |
| SAST | **bandit** | security anti-patterns | CI step |
| SCA | **pip-audit** | known-vulnerable dependencies + license | CI step |
| CI | **GitHub Actions** | matrix 3.11/3.12, artifacts | `.github/workflows/quality.yml` |
| Pre-commit | **pre-commit** | catch issues before push | `.pre-commit-config.yaml` |

## The CI pipeline (7 stages)

```
ruff-check → ruff-format → mypy → pytest-cov → mutmut → bandit → pip-audit
```

Then the gate itself runs on the golden set and uploads `reports/` as an
artifact so every run keeps its evidence.

## Why this stack

- **OSS, self-hostable, no vendor lock-in** for the reference repo: a reviewer
  can run everything locally.
- **Code-first runner + CI** is the de-facto pattern (`promptfoo`/`DeepEval`
  style). A hosted platform (Langfuse/Braintrust) is added later only when
  several people need to review results together.
- **Zero runtime dependencies** for the harness core (stdlib only), so the gate
  stays cheap and portable.

## Note on this environment

The development machine used to author this repo has no pytest/ruff/mypy
installed (constraint: no installs). The core behaviour is validated locally
with `python3 scripts/run_stdlib_checks.py`; the full toolchain runs in CI.
