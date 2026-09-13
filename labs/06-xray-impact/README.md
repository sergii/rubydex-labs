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

Before Codex starts, the workflow removes `ground-truth.json` from the sample checkout. Conditions A and B also have the Lab 06 `knowledge/` and `skills/` directories removed. Condition C keeps those two directories and is explicitly instructed to load them.

Rubydex MCP indexing for B and C is scoped to `labs/06-xray-impact/fixture`, so benchmark documentation, knowledge, skills, and ground truth are not part of the semantic index.

## Expected interpretation

A useful result is not necessarily "C wins everything". The interesting split is:

- B should improve structural completeness and/or reduce exploration cost;
- C should improve risk interpretation, explicit policy detection, and the deploy recommendation;
- if B adds little over A, modern source-search agents may already be good enough for this fixture and we should increase structural ambiguity/scale before making a stronger claim.
