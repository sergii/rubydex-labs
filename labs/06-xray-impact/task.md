# Task: X-Ray a proposed checkout change

Work only from the current fixture source. Do not edit files, run Rails, run tests, install dependencies, or inspect parent benchmark files. Do not use Rubydex or another semantic-index tool.

A developer proposes this change in `Orders::Checkout`:

```diff
- Payments::CaptureJob.perform_later(@order.id)
+ Payments::Capture.call(@order.id)
```

Your job is not to explain Ruby syntax. Produce a consequence-oriented X-Ray for a human engineer: what is affected, what can go wrong operationally, what must be verified, and whether you can establish any explicit company-policy violation from the evidence available to you.

Use only IDs from the candidate vocabularies below for the first three sections. Select an ID only when the repository gives you a concrete reason to believe the proposed change affects it.

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

If the repository itself establishes an explicit company policy ID that this change violates, return each `POLICY-*` ID on its own line. Otherwise return exactly:

```text
NONE
```

Do not invent policy IDs from general engineering practice.

## Recommendation

Return exactly one of:

```text
SAFE
CAUTION
BLOCK
```

Base the recommendation only on evidence actually available in this condition. Prefer `CAUTION` over inventing an unknown company rule.
