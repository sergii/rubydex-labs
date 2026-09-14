# Lab 13 — evidence fusion

> **Status: DESIGNED — COMPARISON BOUNDARY FROZEN OFFLINE — MODEL BENCHMARK NOT RUN**

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
ComparisonRecord
        ↓
optional ConflictRecord / Finding / Derived assertion
        ↓
model explanation
```

## Comparison before conflict

Lab 13 now makes `ComparisonRecord` first-class.

```text
Assertion A + Assertion B
        ↓
ComparisonRecord
        ↓
conflict_state = NONE | EXPLAINED | ACTIVE | RESOLVED
        ↓
optional ConflictRecord
```

This fixes a conceptual weakness in the older conflict model, where benign differences such as scope or temporal mismatch were stored inside an object called `ConflictRecord`.

The new contract separates:

```text
comparison_class
```

from:

```text
conflict_state
```

so a difference can be preserved without falsely implying contradiction.

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

Lab 13 uses:

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

`schemas/comparison.schema.json` records both the class and the conflict state.

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

An observed call does not prove the architecture declaration is complete, and an allowed dependency does not prove a call happened.

But:

```text
allowed_dependency_only(A,B)
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

The deterministic corpus covers:

1. compatible semantic/runtime evidence;
2. declared-vs-observed drift;
3. same-name/different-identity;
4. revision mismatch;
5. environment mismatch;
6. deterministic contradiction;
7. non-overlapping runtime windows;
8. independent corroboration.

Mutation tests additionally try to manufacture false conflicts by changing environment, revision, valid time, entity identity, and predicate semantics.

## Machine-owned invariants

1. Source assertions remain immutable inputs.
2. Fusion never rewrites assertion kind.
3. Fusion never discards provenance.
4. Different truth domains are not collapsed into one claim.
5. Name equality never establishes identity.
6. Scope mismatch blocks contradiction classification.
7. Temporal/revision mismatch blocks contradiction classification unless the task explicitly compares change over time.
8. `CONTRADICTION` requires aligned identity, comparable predicate semantics, overlapping scope/time, and incompatible values/relations.
9. `ComparisonRecord` exists even when no conflict exists.
10. Benign comparison classes have `conflict_state = NONE` and no `conflict_ref`.
11. Active contradictions/drift have `conflict_state = ACTIVE` and an explicit conflict reference.
12. A conflict/finding never deletes the source assertions that produced it.

## Offline execution

Canonical command:

```bash
make lab13-self-test
```

It performs zero model/API calls and runs:

```text
1. frozen comparator fixtures
2. false-conflict mutation tests
3. ComparisonRecord → ConflictRecord boundary tests
```

The current offline harness is intended to prove machine semantics, not model quality.

## Later model comparison

A future explicitly authorized experiment may compare:

```text
M1 = model receives raw heterogeneous evidence
M2 = model receives normalized assertions
M3 = model receives normalized assertions + deterministic ComparisonRecord
```

Expected semantic ordering:

```text
M3 >= M2 > M1
```

No such model result exists yet.

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
- ComparisonRecord/ConflictRecord gating correctness.

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

## World-model implication

Lab 13 validates this boundary:

```text
Evidence
  ↓
Assertion
  ↓
Identity + semantic + scope/time alignment
  ↓
ComparisonRecord
  ↓
optional ConflictRecord
  ↓
optional Derived Assertion / Finding
```

The graph shown to a human remains a projection of these objects, not the source of truth.

## Architecture cleanup result

The earlier design-review hypothesis is now strong enough to use going forward:

> `ComparisonRecord` is the broad epistemic relation between assertions; `ConflictRecord` is a narrower projection for active/resolved conflicts.

The existing v1 conflict schema remains untouched for compatibility during Lab 13. New code should prefer the comparison-first boundary rather than adding more benign mismatch classes to `ConflictRecord`.

This lab still does not justify a destructive schema migration. It establishes the direction for later cleanup.

## Safety / execution

The offline deterministic harness makes zero model/API calls.

Real model execution remains disabled unless repository spend authorization and explicit user authorization for a new run are both present.

## Stop condition

Do not solve fusion by asking the model to "reason carefully" over raw heterogeneous evidence. First make identity, predicate semantics, scope, time, provenance, comparison class, and conflict state machine-visible.

See [`../../docs/comparison-model.md`](../../docs/comparison-model.md), [`../../schemas/comparison.schema.json`](../../schemas/comparison.schema.json), [`../../docs/world-model.md`](../../docs/world-model.md), [`../../docs/identity-model.md`](../../docs/identity-model.md), and [`../../docs/conflict-model.md`](../../docs/conflict-model.md).
