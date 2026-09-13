# Payment architecture knowledge

The checkout payment flow is revenue-critical.

## Explicit policies

- `POLICY-PAY-007`: every successful provider capture must record the provider payment in `Payments::Ledger` and confirm the order before the capture path is considered complete.
- `POLICY-AUD-002`: every successful provider capture must emit the payment audit event used by reporting/reconciliation.

A change that can charge the customer while skipping either policy is a deployment blocker.
