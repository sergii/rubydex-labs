# OpenAI API spend safety

The repository keeps real OpenAI API execution **disabled by default**.

## Master switch

All GitHub Actions workflows that can spend real OpenAI API balance are gated by the repository Actions variable:

```text
RUN_WITH_REAL_OPENAI_API
```

Only the literal value:

```text
true
```

enables API-spending jobs. A missing variable, an empty value, `false`, or any other value keeps those jobs skipped.

`OPENAI_API_KEY` may remain configured in repository Actions secrets while the master switch is disabled. Possessing the secret is not treated as authorization to spend API balance.

## Guarded workflows

The master switch protects:

- `.github/workflows/benchmark.yml`
- `.github/workflows/xray-benchmark.yml`
- `.github/workflows/ondemand-benchmark.yml`
- `.github/workflows/task-shape-benchmark.yml`
- `.github/workflows/autonomous-escalation-benchmark.yml`
- `.github/workflows/deterministic-routing-benchmark.yml`
- `.github/workflows/natural-language-routing-benchmark.yml`
- `.github/workflows/evidence-planner-benchmark.yml`

The older benchmark workflows use two layers of protection:

1. expensive benchmark jobs have a job-level condition requiring `vars.RUN_WITH_REAL_OPENAI_API == 'true'`;
2. before any Codex/OpenAI execution, `scripts/ci/assert-real-openai-api-enabled.sh` checks both the master switch and the presence of `OPENAI_API_KEY`.

Direct Responses API scripts also defend themselves. `scripts/ci/classify-evidence-route.py` and `scripts/ci/plan-evidence.py` refuse a real API call unless their process environment contains `RUN_WITH_REAL_OPENAI_API=true`.

Lab 11 adds a third layer: its manual workflow input `confirm_api_spend` must also be `true`.

## Disabled behavior

When the switch is missing or disabled:

```text
configuration / offline validation may run
API-spending matrix jobs are skipped
aggregate jobs that depend on real samples are skipped
OpenAI API calls = 0
```

This is intentionally a graceful skip rather than a failing CI signal.

## Enabling a benchmark intentionally

1. Open repository **Settings → Secrets and variables → Actions → Variables**.
2. Set `RUN_WITH_REAL_OPENAI_API` to `true`.
3. Run the desired benchmark intentionally.
4. For Lab 11, also set the manual `confirm_api_spend` input to `true`.
5. After the experiment, set `RUN_WITH_REAL_OPENAI_API` back to `false` or remove the variable.

## Design rule

Real API capability and authorization to spend are separate concerns:

```text
OPENAI_API_KEY                 = capability
RUN_WITH_REAL_OPENAI_API=true  = authorization
```

A workflow or script must not infer spending authorization merely because an API key is available.
