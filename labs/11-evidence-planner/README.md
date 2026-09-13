# Lab 11 — multi-backend evidence planner

> **Status: DESIGNED — NOT RUN**
>
> This lab is intentionally committed before measurement. No benchmark result exists yet. Run it only after OpenAI API spending is explicitly re-enabled.

## Goal

Lab 10 proved that a small classifier can recover a **single primary evidence class** from an ordinary engineering request. Real engineering questions often require more than one truth source.

Lab 11 asks the next question:

> Can a low-cost planner turn a natural-language engineering request into a minimal, reliable, multi-backend `EvidencePlan`?

The target production-shaped flow is:

```text
engineering request
        |
        v
 Evidence Planner
        |
        v
 EvidencePlan
   /       |        |        \
source  semantic  runtime  architecture
   \       |        |        /
        evidence backends
             |
             v
          EvidenceSets
             |
             v
            model
```

This lab tests **planning only**. It does not execute the downstream evidence backends. That keeps the experiment cheap and isolates whether the planner selected the right evidence classes before we spend money on source traversal, Rubydex, runtime queries, or architecture retrieval.

## Evidence classes

The planner may select one or more of:

```text
SOURCE_LOCAL
SEMANTIC_RELATIONSHIP_SET
RUNTIME_BEHAVIOR
ARCHITECTURE_KNOWLEDGE
```

- `SOURCE_LOCAL` — local source/declaration/method facts.
- `SEMANTIC_RELATIONSHIP_SET` — complete resolved repository-wide structural sets.
- `RUNTIME_BEHAVIOR` — observed traces, metrics, logs, latency, retries, errors, or production behavior.
- `ARCHITECTURE_KNOWLEDGE` — ownership, capabilities, intended boundaries, policies, and declared dependencies.

The machine-readable contract is [`../../schemas/evidence-plan.schema.json`](../../schemas/evidence-plan.schema.json).

## Conditions

```text
P = planner sees only the raw engineering request and produces an EvidencePlan
O = frozen oracle plan in ground-truth.json; not an API condition
```

The oracle is used only for scoring. It is never passed to the planner.

Unlike Lab 10, there is no need to pay for a second model condition that merely replays oracle labels. The benchmark question is whether `P` recovers the required evidence set with low over-routing.

## Frozen request corpus

[`requests.json`](requests.json) contains 12 requests:

- four single-backend requests, one per evidence class;
- eight multi-backend requests requiring two, three, or four evidence classes.

[`ground-truth.json`](ground-truth.json) freezes, per request:

- required evidence classes;
- allowed optional classes;
- expected planning strategy.

The corpus intentionally includes questions such as safety, production regressions, deletion risk, ownership, policy, and pre-deploy X-Ray analysis where a single-class router cannot represent the full answer requirements.

## Measurements

Primary correctness metrics:

- schema-valid plan;
- required-class recall;
- exact required-class set;
- over-routing rate;
- optional-route validity;
- duplicate-class violations;
- expected strategy match.

Efficiency metrics:

- planner latency;
- input/output/reasoning/total tokens;
- estimated planner API cost.

The most important benchmark metric is:

> **required evidence recall without unnecessary backend fan-out**

A planner that chooses every backend for every request is not correct even if recall is 100%.

## Hypothesis

A low-reasoning planner should recover the required evidence set for most or all frozen requests at roughly the same order of cost as the Lab 10 classifier, while correctly producing multi-backend plans that Lab 10's single-label classifier cannot express.

If this holds, the next experiment should execute those plans against real evidence backends and measure whether the planner actually reduces end-to-end cost while preserving correctness.

## API spending safety gate

This workflow is deliberately impossible to run accidentally from a commit:

1. `.github/workflows/evidence-planner-benchmark.yml` has **only** `workflow_dispatch`; there is no `push` trigger.
2. Repository Actions variable `RUN_WITH_REAL_OPENAI_API` must equal the literal string `true`.
3. The manual workflow input `confirm_api_spend` must also be checked.
4. `scripts/ci/plan-evidence.py` independently refuses to call OpenAI unless its process environment contains `RUN_WITH_REAL_OPENAI_API=true`.
5. `OPENAI_API_KEY` is read only inside the gated benchmark job.

When the repository variable is missing or false, the workflow may run its local validation/guard jobs, but **the planner matrix is skipped and no OpenAI API call is made**.

Recommended default state:

```text
RUN_WITH_REAL_OPENAI_API=false
```

When budget is available and this lab is ready to measure:

```text
RUN_WITH_REAL_OPENAI_API=true
```

Then manually dispatch **Lab 11 evidence planner benchmark** with `confirm_api_spend=true`.

After the run, return the repository variable to `false`.

## Planned run

The first publishable run should use:

```text
model: gpt-5.6-luna
reasoning: low
repetitions: 3
requests: 12
planned API calls: 36
```

No downstream Codex agent or Rubydex traversal runs in Lab 11, so this should remain substantially cheaper than Labs 07–10.

## Exit criteria

Lab 11 is ready to graduate to backend execution when:

- required-class recall is high enough to avoid silently missing a truth source;
- exact required-class-set accuracy is stable across repetitions;
- over-routing stays low;
- multi-backend tasks are materially better represented than with a single-label router;
- planner cost remains negligible relative to downstream evidence acquisition.

## Current status

**DESIGNED — NOT RUN.**

Do not add a benchmark result file until a real gated run has completed.
