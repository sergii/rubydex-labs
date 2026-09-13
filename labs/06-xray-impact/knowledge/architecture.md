# Checkout and payments architecture knowledge

This file is trusted company engineering knowledge for the benchmark fixture. It describes intent that is not reliably derivable from Ruby source alone.

## Critical flow

`Orders::Checkout` is a customer request-path operation. Its payment sequence is:

```text
reserve inventory
-> mark payment pending
-> enqueue payment capture
-> capture provider payment
-> record payment ledger
-> confirm order
-> enqueue receipt
```

Checkout has a p95 server-side latency budget of 400 ms. External payment-provider latency is intentionally excluded from that request budget.

## Infrastructure

`Payments::CaptureJob` runs on the Sidekiq `payments` queue backed by Redis. That queue is the retry, capacity-isolation, and operational-observability boundary for payment capture.

`Payments::Capture` talks to Stripe through `Payments::StripeGateway` and persists capture state through `Payments::Ledger` in PostgreSQL.

A provider timeout is ambiguous: Stripe may have accepted a capture before the client observes the timeout. Retrying a capture is expected and must reuse the same provider idempotency key.

## Explicit policies

### POLICY-REQ-001 - no payment-provider I/O on the customer request path

Customer request-path code must not synchronously call an external payment provider. Payment-provider I/O must execute behind an asynchronous reliability boundary so provider latency/failure cannot directly consume request workers or determine request latency.

### POLICY-PAY-004 - capture enters through the capture job

Production order capture must enter through `Payments::CaptureJob`. The job owns the approved retry policy for `Payments::ProviderTimeout` and the `payments` queue is the approved capacity/observability boundary. Direct request-path invocation of `Payments::Capture` violates this policy.

### POLICY-PAY-006 - stable capture idempotency key

Retries for the same order capture must use the stable key `order:<order_id>:capture`. The current `Payments::Capture` implementation satisfies this policy. The proposed caller change does not, by itself, violate this policy.

## Deploy rule

A change that violates `POLICY-REQ-001` or `POLICY-PAY-004` is `BLOCK` until the design is changed or the policy is explicitly superseded through architecture review.
