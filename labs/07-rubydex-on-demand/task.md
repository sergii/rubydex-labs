# Task: X-Ray a payment gateway change

Work only from the current fixture source plus the supplied architecture knowledge and skill. Do not edit files, run Rails, run tests, install dependencies, inspect ground truth, or inspect unrelated filesystem locations.

A developer proposes this change in `Payments::ProviderGateway#charge`:

```diff
 def charge(order)
   result = provider.charge(order)
-  after_capture(order, result)
   result
 end
```

Determine the human-facing consequences of this change. Trace real Ruby structure carefully: callers may reach the method through inheritance, aliases, delegation, or reopened classes. Ignore lexical decoys that are not structurally connected.

Use exactly these candidate IDs.

Impact candidates:

```text
IMPACT-CHECKOUT
IMPACT-PAYMENT-CAPTURE
IMPACT-PAYMENT-LEDGER
IMPACT-ORDER-CONFIRMATION
IMPACT-PAYMENT-RECEIPT
IMPACT-PAYMENT-REPORTING
IMPACT-STRIPE
IMPACT-REFUNDS
IMPACT-SEARCH
IMPACT-ADMIN
```

Risk candidates:

```text
RISK-CHARGED-NOT-RECORDED
RISK-CHARGED-ORDER-UNCONFIRMED
RISK-MISSING-RECEIPT
RISK-MISSING-AUDIT
RISK-RECONCILIATION-DRIFT
RISK-SQL-INJECTION
RISK-NPLUSONE
RISK-CACHE-STAMPEDE
```

Verification candidates:

```text
VERIFY-SUCCESSFUL-CAPTURE
VERIFY-LEDGER-WRITE
VERIFY-ORDER-CONFIRMATION
VERIFY-PAYMENT-RECEIPT
VERIFY-AUDIT-EVENT
VERIFY-LEGACY-GATEWAY
VERIFY-SEARCH
VERIFY-REFUND
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
Return exactly one of `SAFE`, `CAUTION`, or `BLOCK`.
