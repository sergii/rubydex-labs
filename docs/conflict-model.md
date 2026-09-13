# Conflict and reconciliation model

This document defines how the evidence-backed world model should represent, classify, and reconcile disagreement between evidence sources and assertions.

The central rule is:

> Disagreement is not always contradiction, and contradiction is not always something to erase.

The system must preserve the dimensions of truth that produced apparently different claims before deciding whether they conflict.

## Why source priority is not enough

A naive system might define a fixed hierarchy such as:

```text
runtime > semantic > architecture > model inference
```

That is unsafe because these sources often answer different questions.

Examples:

```text
Rubydex: A may reference B
OTEL:    A did not call B in the last hour
```

These are compatible. One describes structural possibility; the other describes observed behavior in a time window.

Likewise:

```text
Architecture: A is allowed to call B
OTEL:        A called C
```

This may indicate architecture drift, but it is not resolved by choosing one source as universally more authoritative.

## Conflict dimensions

Before comparing assertions, the system must align:

- identity;
- predicate semantics;
- scope;
- revision;
- environment;
- valid time;
- evidence class;
- completeness/freshness assumptions.

Only assertions that address the same proposition under compatible scope can directly contradict one another.

## Conflict classes

### NON_CONFLICTING_DIFFERENCE

Assertions describe different dimensions of reality.

Example:

```text
DETERMINISTIC: A may depend on B
OBSERVED:      A did not call B during window W
```

No conflict.

### SCOPE_MISMATCH

Assertions differ because scope differs.

Example:

```text
OBSERVED prod:    checkout -> calls -> payments
OBSERVED staging: checkout -> calls -> fake-payments
```

No direct contradiction.

### TEMPORAL_MISMATCH

Assertions were valid at different times or revisions.

Example:

```text
revision abc: Payments::Gateway exists
revision def: PaymentProvider exists
```

Potential rename/evolution, not automatically conflict.

### DECLARED_VS_OBSERVED_DRIFT

Declared architecture or policy does not match observed runtime behavior.

Example:

```text
DECLARED: checkout may call payments-v2
OBSERVED: checkout called legacy-payments
```

This should usually become a Finding rather than be silently reconciled.

### DETERMINISTIC_CONTRADICTION

Two deterministic sources under the same scope claim incompatible facts.

This is severe and usually indicates one of:

- stale evidence;
- mismatched revisions;
- backend bug;
- identity-resolution bug;
- incomplete filtering;
- schema/ingestion error.

The system should not auto-pick a winner without a specific reconciliation rule.

### OBSERVATION_CONTRADICTION

Runtime observations appear incompatible after normalizing time/window and identity.

Possible causes include sampling, partial telemetry, multiple instances, deployment overlap, or instrumentation defects.

### IDENTITY_CONFLICT

Two evidence paths disagree about what an observation refers to.

Identity conflicts must be resolved before higher-level assertion reconciliation.

### POLICY_CONFLICT

Two active declared policies establish incompatible requirements for the same scope.

This is organizational/architecture inconsistency and should generally be surfaced.

### DERIVATION_CONFLICT

A derived assertion conflicts with its supporting lower-level assertions or with a stronger independently established fact.

Derived claims are candidates for recomputation, not authoritative winners.

### PREDICTION_MISS

A PREDICTED assertion is contradicted by later OBSERVED evidence.

The prediction should remain in history and receive an evaluated outcome such as `REFUTED`, not be rewritten.

## Reconciliation outcomes

A reconciliation process may produce:

```text
COMPATIBLE
SUPERSEDE_OLDER
PREFER_MORE_SPECIFIC_SCOPE
PREFER_FRESHER_OBSERVATION
RECOMPUTE_DERIVED
REQUIRE_IDENTITY_RESOLUTION
REQUIRE_MORE_EVIDENCE
MARK_CONFLICTED
CREATE_FINDING
HUMAN_REVIEW
```

The outcome is separate from the conflict class.

## Source authority is predicate-specific

Authority should be attached to proposition type rather than to the source globally.

Examples:

```text
resolved code references at revision X
    -> semantic backend is authoritative

observed p95 latency during window W
    -> telemetry backend is authoritative

allowed dependency / owner / policy
    -> declared architecture source is authoritative

what changed between revisions
    -> Git/change evidence is authoritative
```

No backend is authoritative for all questions.

## Findings from conflicts

Some disagreements are themselves high-value product outputs.

Examples:

```text
Architecture Drift
Declared dependency differs from observed dependency.

Ownership Drift
Runtime/service ownership differs from declared catalog ownership.

Telemetry Gap
Semantic/runtime expectation exists but no sufficient observation is available.

Stale Knowledge
Declared assertion remains active beyond its supported revision/time.

Identity Ambiguity
Cross-sensor evidence cannot be safely fused because entity mapping is unresolved.

Prediction Miss
A pre-deploy predicted consequence was not observed, or an unpredicted consequence occurred.
```

A conflict detector therefore feeds Findings; reconciliation is not merely internal cleanup.

## Preserve both sides

When a real conflict exists, the default behavior is append-only:

```text
Assertion A
Assertion B
Conflict record linking A and B
Resolution / finding
```

Do not overwrite either assertion merely to make the current graph look consistent.

## Conflict and confidence

Conflict changes belief state, not just score.

A proposition with strong support on both sides should become `CONFLICTED`, not an averaged 0.5.

Reconciliation may later move it to another state if new evidence explains the discrepancy.

## Iterative evidence acquisition

Conflict can trigger a new EvidencePlan step.

Example:

```text
DECLARED: checkout -> payments-v2
OBSERVED: checkout -> legacy-payments
       |
       v
conflict classifier
       |
       v
need deployment/change evidence
       |
       v
Git / deploy history
```

The planner should ask for the cheapest evidence capable of distinguishing likely causes.

## Working invariant

> Never collapse disagreement before aligning identity, scope, time, predicate semantics, and truth source. Some conflicts should be resolved; some should be preserved; some are the product finding.