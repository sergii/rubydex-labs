# Lab 13 — evidence fusion

> **Status: DESIGNED — OFFLINE HARNESS IN PROGRESS — MODEL BENCHMARK NOT RUN**

## Research question

Can evidence from different sensors be combined without collapsing distinct claim semantics, and can the system distinguish compatible evidence, scope/time mismatch, identity ambiguity, drift, and genuine contradiction before a model explains consequences?

Lab 13 is not primarily a test of whether an LLM can summarize several sources. It tests whether the machine layer can preserve the meaning of each assertion while comparing them safely.

## Core invariant

> Similar-looking graph edges are not necessarily the same claim.

For example:

```text
DETERMINISTIC
Payments::CaptureJob --references--> Payments::Gateway

DECLARED
checkout-service --allowed_dependency--> payments-api

OBSERVED
checkout-service --called--> payments-api
```

These may all be relevant to the same engineering question, but they must not be collapsed into one generic `depends_on` edge.

The fusion pipeline is:

```text
EvidenceSets / sensor records
        ↓
Assertions with preserved kind + provenance
        ↓
Identity alignment
        ↓
Predicate semantic alignment
        ↓
Scope / revision / environment / valid-time alignment
        ↓
Comparison classification
        ↓
optional Conflict / Finding / Derived assertion
        ↓
model explanation
```

## What Lab 13 must prove

The deterministic layer should be able to answer, before model reasoning:

1. Are these assertions about the same durable entities?
2. Are the predicates semantically comparable?
3. Do their scopes overlap?
4. Do their revisions / valid times overlap?
5. Are they compatible, merely different, or actually contradictory?
6. Is the disagreement itself an engineering finding such as architecture drift?

If those questions are unresolved, the system must preserve uncertainty rather than force a fused fact.

## Comparison states

Lab 13 uses a comparison layer before a conflict layer.

```text
COMPATIBLE
NON_COMPARABLE_PREDICATE
IDENTITY_UNRESOLVED
SCOPE_MISMATCH
TEMPORAL_MISMATCH
REVISION_MISMATCH
ENVIRONMENT_MISMATCH
DECLARED_VS_OBSERVED_DRIFT
CONTRADICTION
INSUFFICIENT_EVIDENCE
```

Only `DECLARED_VS_OBSERVED_DRIFT` and `CONTRADICTION` are conflict-like outcomes by default. The others are alignment or comparability outcomes.

This intentionally fixes the conceptual weakness identified in the architecture review, where `Conflict` currently also contains benign mismatch classes.

## Predicate semantics

Predicate strings must not be matched only by spelling.

Examples:

```text
references
allowed_dependency
called
owns
must_produce
observed_produced
```

A semantic relation table defines whether two predicates are:

```text
EQUIVALENT
COMPATIBLE_DIFFERENT_TRUTH_DOMAIN
POTENTIALLY_CONTRADICTORY
NON_COMPARABLE
```

Example:

```text
allowed_dependency vs called
= COMPATIBLE_DIFFERENT_TRUTH_DOMAIN
```

An observed call does not prove the architecture declaration is complete, and an allowed dependency does not prove a call happened.

But:

```text
allowed_dependency(A,B)
observed called(A,C)
where policy says ONLY B is allowed
```

may produce architecture drift after scope/time/identity alignment.

## Identity boundary

Name equality is insufficient.

```text
payments-api
payments-api
```

may refer to different deployment units, environments, historical entities, or representations.

Comparisons use stable entity IDs when resolved. If stable identity is unavailable or conflicting, result is `IDENTITY_UNRESOLVED`; the system must not silently compare by name.

Lab 13 therefore treats identity resolution as a prerequisite, not part of the model's prose reasoning.

## Scope and time alignment

Two assertions can both be true while disagreeing textually because their scopes differ.

Examples:

```text
production vs staging
region:eu vs region:us
revision abc123 vs def456
2026-09-10..2026-09-11 vs 2026-09-14
```

A conflict is impossible to establish until the relevant dimensions overlap or are explicitly comparable.

## Frozen offline scenarios

The initial deterministic corpus should cover at least these cases:

1. `semantic-and-runtime-compatible` — deterministic code relationship and observed runtime call are distinct but compatible.
2. `declared-and-observed-drift` — architecture allows B, runtime observes unexpected C under the same scope.
3. `same-name-different-identity` — names match but entity IDs differ; must not fuse.
4. `same-fact-different-revision` — contradictory-looking facts are separated by revision.
5. `same-fact-different-environment` — production and staging differ without conflict.
6. `deterministic-contradiction` — two machine sources establish mutually exclusive values in aligned scope.
7. `observations-from-different-windows` — runtime observations differ across non-overlapping windows.
8. `corroborating-independent-sources` — two independent sources support the same aligned assertion.
9. `derived-consequence-from-compatible-claims` — compatible assertions support a derived consequence without replacing their originals.
10. `policy-violation` — declared policy and observed behavior align sufficiently to produce a Finding candidate.

## Machine-owned invariants

1. Source assertions remain immutable inputs.
2. Fusion never rewrites assertion kind.
3. Fusion never discards provenance.
4. Different truth domains are not collapsed into one claim.
5. Name equality never establishes identity.
6. Scope mismatch blocks contradiction classification.
7. Temporal/revision mismatch blocks contradiction classification unless the task explicitly compares change over time.
8. `CONTRADICTION` requires aligned identity, comparable predicate semantics, overlapping scope/time, and incompatible values/relations.
9. A derived assertion references all required input assertions.
10. A conflict/finding never deletes the source assertions that produced it.

## Proposed offline conditions

Lab 13 first tests deterministic comparison only:

```text
D0 = raw assertions displayed side by side
D1 = deterministic alignment + comparison
D2 = deterministic alignment + comparison + derived finding candidate
```

No LLM is required for D0–D2.

A later, explicitly authorized model experiment may compare:

```text
M1 = model receives raw heterogeneous evidence
M2 = model receives normalized assertions
M3 = model receives normalized assertions + deterministic comparison result
```

Expected ordering for semantic correctness:

```text
M3 >= M2 > M1
```

but no model result exists until explicitly run.

## Metrics

Primary deterministic metrics:

- identity alignment accuracy;
- predicate comparability accuracy;
- scope/time alignment accuracy;
- comparison-class exact accuracy;
- false-conflict rate;
- missed-conflict/drift rate;
- provenance retention;
- source assertion preservation;
- derived assertion lineage completeness.

Critical metric:

> false conflict rate must be extremely low.

A system that aggressively invents contradictions from differently scoped truths is worse than one that admits uncertainty.

## Fail-closed rules

When identity is unresolved:

```text
IDENTITY_UNRESOLVED
```

not `CONTRADICTION`.

When predicate semantics are unknown:

```text
NON_COMPARABLE_PREDICATE
```

not generic edge fusion.

When scope or time cannot be aligned:

```text
SCOPE_MISMATCH / TEMPORAL_MISMATCH / INSUFFICIENT_EVIDENCE
```

not a confident finding.

## Relationship to the world model

Lab 13 validates this boundary:

```text
Evidence
  ↓
Assertion
  ↓
Identity + semantic + scope/time alignment
  ↓
Comparison
  ↓
Conflict / Derived Assertion / Finding
```

The graph shown to a human is a projection of these objects, not the source of truth.

## Relationship to architecture cleanup

This lab should produce evidence for two pending design questions:

1. whether `identity-link.schema.json` should be narrowed to true identity/representation relations and move `OWNED_BY`, `SERVES_CAPABILITY`, `IMPLEMENTED_BY`, etc. into ordinary assertions;
2. whether `conflict.schema.json` should evolve into a broader comparison record plus a narrower conflict record.

Do not migrate those schemas merely because the cleanup appears conceptually attractive. Use Lab 13 cases to validate the boundary first.

## Safety / execution

The offline deterministic harness must make zero model/API calls.

Real model execution remains disabled unless repository spend authorization and explicit user authorization for a new run are both present.

## Stop condition

Do not solve fusion by asking the model to "reason carefully" over raw heterogeneous evidence. First make identity, predicate semantics, scope, time, and provenance machine-visible.

See [`../../docs/world-model.md`](../../docs/world-model.md), [`../../docs/identity-model.md`](../../docs/identity-model.md), [`../../docs/conflict-model.md`](../../docs/conflict-model.md), [`../../schemas/assertion.schema.json`](../../schemas/assertion.schema.json), and [`../../docs/design-review.md`](../../docs/design-review.md).
