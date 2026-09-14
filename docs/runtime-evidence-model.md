# Runtime evidence model

Runtime telemetry is evidence about observed behavior within a bounded scope and time window. It is not a timeless description of system behavior.

## Core rule

> Observation establishes presence more easily than absence.

A sampled trace proving that a call happened can support a positive `OBSERVED` assertion. Failing to see that call in sampled or partial data normally cannot support a negative assertion.

## Runtime evidence pipeline

```text
runtime sensor
→ immutable evidence
→ identity resolution
→ coverage / sampling evaluation
→ OBSERVED assertion
→ comparison with deterministic / declared assertions
→ optional conflict / finding
```

## Coverage semantics

Runtime evidence should preserve one of:

- `COMPLETE_FOR_SCOPE` — exhaustive only for the explicitly stated scope and window;
- `PARTIAL` — known incomplete collection;
- `SAMPLED` — a subset selected by a sampling mechanism;
- `UNKNOWN` — completeness cannot be established.

Completeness never propagates beyond its scope. A complete observation for one region, route, tenant, environment, service, or window is not complete for another.

## Sampling

Sampling rate is metadata, not epistemic permission.

A 99% sample may still miss a rare event. Therefore large sample count or high sampling rate does not by itself authorize exhaustive negative claims.

## Time

Every runtime-derived assertion is bounded by `valid_time`.

A later observation should create a new assertion rather than rewriting the earlier assertion. This lets Lab 15 reason about change over time without destroying history.

## Identity

Runtime labels such as `service.name`, pod name, container name, hostname, route, or process name are representations and observations, not automatically durable identity.

If identity cannot be resolved safely, preserve the runtime representation and request identity resolution rather than fusing by name.

## Presence / absence examples

Allowed from sampled evidence:

```text
OBSERVED checkout-service --called--> payments-api
```

if at least one sampled trace contains that call.

Normally forbidden from sampled evidence:

```text
OBSERVED checkout-service --did_not_call--> payments-api
```

merely because no sampled trace contained it.

Allowed only with a complete scoped observation contract:

```text
OBSERVED api --health_check_failures--> 0
```

for the exact check set and exact bounded window that was exhaustively accounted for.

## Relationship to confidence

Coverage, sampling, and identity resolution affect the evidence behind an assertion. They should influence structured confidence/belief, not be collapsed into a decorative probability.

`OBSERVED` means the source is runtime observation. It does not mean the claim is globally complete or permanently true.

## Design constraint

Do not add a separate durable `RuntimeObservation` object unless Evidence + Assertion demonstrably lose required semantics. Runtime-specific collection details may remain in evidence provenance / assertion metadata while stable reasoning semantics remain in the shared world model.
