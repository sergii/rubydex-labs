# Skill: analyze an async payment-boundary change

Use this skill only after establishing the actual source/semantic path around the proposed change.

When a change replaces an asynchronous payment job with a direct service call, inspect these consequence classes:

1. **Request latency** - does provider latency move onto a customer request worker?
2. **Failure propagation** - do provider exceptions now fail the caller instead of the job?
3. **Retry semantics** - which retry/discard behavior existed on the job and what replaces it?
4. **Capacity isolation** - is work moving from a bounded queue/worker pool to request capacity?
5. **Ambiguous timeout safety** - can a provider accept the charge while the caller sees a timeout, and is retry idempotent?
6. **Observability** - does queue depth/retry/dead-job monitoring stop covering the operation?
7. **Downstream correctness** - are ledger recording and order confirmation still performed exactly once after a successful capture?

For verification, prefer scenarios that distinguish the old boundary from the new one: success, provider timeout, hard decline, retry behavior, request latency under a slow provider, idempotent retry after an ambiguous timeout, downstream confirmation, and proof that the queue is intentionally bypassed or retained.

Do not add generic risks such as SQL injection, N+1 queries, cache stampedes, or webhook-signature problems unless the code change gives direct evidence for them.
