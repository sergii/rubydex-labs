# Task: X-Ray a proposed checkout change

Work only from the current fixture source plus the two explicitly supplied knowledge artifacts. Do not edit files, run Rails, run tests, install dependencies, inspect ground truth, or inspect unrelated parent benchmark files.

A developer proposes this change in `Orders::Checkout`:

```diff
- Payments::CaptureJob.perform_later(@order.id)
+ Payments::Capture.call(@order.id)
```

First use Rubydex semantic tools to resolve and inspect the declarations/references around `Orders::Checkout`, `Payments::CaptureJob`, and `Payments::Capture`.

Then load exactly these additional knowledge artifacts:

```text
../knowledge/architecture.md
../skills/async-payment-boundary/SKILL.md
```

Use semantic/source evidence for what the code does and the supplied knowledge for company intent/policy. Do not treat general best practice as an explicit company policy unless the knowledge artifact gives it a policy ID.

Use only IDs from the candidate vocabularies below for the first three sections.

Impact candidates:

```text
IMPACT-CHECKOUT
IMPACT-PAYMENT-CAPTURE
IMPACT-PAYMENT-LEDGER
IMPACT-ORDER-CONFIRMATION
IMPACT-PAYMENTS-QUEUE
IMPACT-REDIS
IMPACT-STRIPE
IMPACT-REFUNDS
IMPACT-REPORTING
IMPACT-ADMIN
IMPACT-SEARCH
IMPACT-WEBHOOK-INGESTION
```

Risk candidates:

```text
RISK-REQUEST-LATENCY
RISK-FAILURE-PROPAGATION
RISK-RETRY-LOSS
RISK-CAPACITY-COUPLING
RISK-TIMEOUT-AMBIGUITY
RISK-QUEUE-OBSERVABILITY
RISK-SQL-INJECTION
RISK-NPLUSONE
RISK-CACHE-STAMPEDE
RISK-WEBHOOK-SIGNATURE
RISK-REFUND-OVERPAYMENT
```

Verification candidates:

```text
VERIFY-SUCCESS
VERIFY-PROVIDER-TIMEOUT
VERIFY-CARD-DECLINE
VERIFY-RETRY-BEHAVIOR
VERIFY-REQUEST-LATENCY
VERIFY-IDEMPOTENT-RETRY
VERIFY-ORDER-CONFIRMATION
VERIFY-QUEUE-BYPASS
VERIFY-REFUND
VERIFY-REPORT-EXPORT
VERIFY-SEARCH
VERIFY-WEBHOOK-SIGNATURE
```

Return these sections exactly:

## Impacts

One selected `IMPACT-*` ID per line, followed by ` | ` and one short consequence.

## Risks

One selected `RISK-*` ID per line, followed by ` | ` and one short consequence.

## Verification

One selected `VERIFY-*` ID per line, followed by ` | ` and one short scenario.

## Policy violations

Return every explicit `POLICY-*` ID from the supplied company knowledge that this proposed change violates, one per line. If none, return `NONE`.

## Recommendation

Return exactly one of:

```text
SAFE
CAUTION
BLOCK
```

Apply the supplied company policies when choosing the recommendation.
