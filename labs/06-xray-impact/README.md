# Lab 06 - X-Ray consequence analysis

## Goal

Test whether a coding agent can move from low-level source inspection to a useful human-facing consequence analysis of a proposed Ruby change.

The proposed change moves payment capture from an asynchronous job boundary into the synchronous checkout path:

```diff
- Payments::CaptureJob.perform_later(@order.id)
+ Payments::Capture.call(@order.id)
```

The benchmark is intentionally not asking for a code review or a list of references. It asks what the change affects, what can go wrong, what should be verified, and whether an explicit company policy is violated.

## Conditions

```text
A = source-only navigation
B = source + Rubydex semantic-first navigation
C = source + Rubydex + architecture knowledge + targeted skill
```

All three conditions get the same proposed change, fixture, model, reasoning effort, and closed impact/risk/verification vocabulary. The closed vocabulary makes scoring deterministic and deliberately gives A a strong baseline.

Condition C additionally receives two machine-readable-ish knowledge artifacts:

```text
knowledge/architecture.md
skills/async-payment-boundary/SKILL.md
```

The frozen ground truth is never available to the agent during a measured run.

## What is scored

The scorer measures exact set precision/recall for:

- impacted flows/components;
- operational/reliability risks;
- verification scenarios;
- explicit policy violations.

It also records the final recommendation (`SAFE`, `CAUTION`, or `BLOCK`).

Policy violations and the final recommendation are reported separately because they depend on company knowledge that A and B intentionally do not receive.

## Why this lab exists

Labs 04 and 05 ask whether semantic navigation improves structural discovery in a real Rails monolith. Lab 06 asks the next question:

> Can semantic code evidence plus explicit engineering knowledge produce a better X-Ray of consequences for a human engineer?

Rubydex should help the agent establish the real execution/dependency neighborhood with fewer exploratory reads. It should not, by itself, know company policy, SLO intent, or why a particular async boundary exists. Condition C tests that missing layer.

## Fixture

The fixture models a small checkout/payment flow:

```text
Orders::Checkout
  -> Payments::CaptureJob
      -> Payments::Capture
          -> Payments::StripeGateway
          -> Payments::Ledger
          -> Orders::Confirm
              -> Notifications::PaymentReceiptJob

StripeWebhooksController
  -> Payments::ReconcileWebhook
      -> Payments::Ledger
      -> Orders::Confirm
```

The benchmark never boots Rails or calls external services. The fixture only exists to provide realistic static evidence.

## Isolation

Each sample runs on a fresh GitHub-hosted VM.

Before the measured agent starts, the workflow copies only the fixture into a clean temporary workspace. Condition C also gets copies of the architecture knowledge and targeted skill inside that workspace. A and B do not. The benchmark directory and Git history are then removed from the measured job, so `ground-truth.json` and the other condition prompts are not locally recoverable by the agent.

Rubydex MCP for B and C indexes only the temporary fixture workspace, so benchmark documentation and ground truth are not part of the semantic index.

## Run on GitHub Actions

The primary runner is the dedicated workflow:

```text
GitHub -> Actions -> Rubydex X-Ray benchmark -> Run workflow
```

Inputs:

- model: defaults to `gpt-5.6-luna`;
- reasoning: `low`, `medium`, or `high`;
- repetitions: `1` or `3` samples per condition.

The default produces nine independent samples:

```text
3 x A - source only
3 x B - Rubydex semantic-first
3 x C - Rubydex + architecture knowledge + skill
```

The aggregate job publishes a Markdown Step Summary and the `xray-benchmark-report` artifact containing `report.md` and `report.json`.

## Expected interpretation

A useful result is not necessarily "C wins everything". The interesting split is:

- B should improve structural completeness and/or reduce exploration cost;
- C should improve risk interpretation, explicit policy detection, and the deploy recommendation;
- if B adds little over A, modern source-search agents may already be good enough for this fixture and we should increase structural ambiguity/scale before making a stronger claim.
