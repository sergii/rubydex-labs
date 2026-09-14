# Comparison model

## Thesis

> Comparison is broader than conflict.

Two assertions may differ because they refer to different identities, predicates, scopes, revisions, environments, valid-time windows, or truth domains. Those differences must be classified before any conflict is created.

The durable order is:

```text
Assertion A + Assertion B
        ↓
ComparisonRecord
        ↓
conflict_state = NONE | EXPLAINED | ACTIVE | RESOLVED
        ↓
optional ConflictRecord
        ↓
optional Finding
```

A `ConflictRecord` is therefore a projection/subset of assertion comparisons, not the universal container for every disagreement.

## Why this boundary exists

The previous conflict schema mixed true contradiction with benign or unresolved comparison outcomes such as:

- non-conflicting difference;
- scope mismatch;
- temporal mismatch;
- identity ambiguity.

This makes downstream reasoning unsafe because a consumer cannot distinguish "these claims contradict each other" from "these claims are not yet comparable" without reinterpreting the record.

`ComparisonRecord` removes that ambiguity.

## Comparison classes

The Lab 13 contract currently uses:

- `COMPATIBLE`
- `NON_COMPARABLE_PREDICATE`
- `IDENTITY_UNRESOLVED`
- `SCOPE_MISMATCH`
- `TEMPORAL_MISMATCH`
- `REVISION_MISMATCH`
- `ENVIRONMENT_MISMATCH`
- `DECLARED_VS_OBSERVED_DRIFT`
- `CONTRADICTION`
- `INSUFFICIENT_EVIDENCE`

These classify what happened during alignment and comparison. They do not by themselves imply incident severity, finding severity, or remediation priority.

## Conflict state

`conflict_state` is deliberately separate from `comparison_class`:

```text
NONE
EXPLAINED
ACTIVE
RESOLVED
```

Examples:

```text
ENVIRONMENT_MISMATCH
→ conflict_state = NONE

TEMPORAL_MISMATCH
→ conflict_state = NONE

IDENTITY_UNRESOLVED
→ conflict_state = NONE

CONTRADICTION
→ conflict_state = ACTIVE

DECLARED_VS_OBSERVED_DRIFT
→ ACTIVE when the declaration is authoritative for the aligned scope
→ otherwise EXPLAINED or NONE depending on policy semantics
```

This keeps ontology and workflow separate.

## Alignment dimensions

Before a conflict may become `ACTIVE`, the comparator must record alignment state for:

- identity;
- predicate semantics;
- scope;
- revision;
- environment;
- valid time;
- truth domain.

Allowed alignment states:

```text
ALIGNED
MISMATCHED
UNKNOWN
NOT_APPLICABLE
```

The conservative rule is:

> Unknown or mismatched comparison dimensions should prevent escalation to contradiction unless the relevant predicate semantics explicitly make that dimension irrelevant.

## ConflictRecord boundary

The existing `schemas/conflict.schema.json` remains a v1 research artifact for compatibility. It should not be destructively migrated during Lab 13.

Going forward, new code should treat `ConflictRecord` as appropriate only when a `ComparisonRecord` has `conflict_state = ACTIVE` or when an already-active conflict is later `RESOLVED`.

Benign differences and unresolved comparability remain ComparisonRecords only.

Conceptually:

```text
ComparisonRecord
├── COMPATIBLE                  → no ConflictRecord
├── ENVIRONMENT_MISMATCH        → no ConflictRecord
├── REVISION_MISMATCH           → no ConflictRecord
├── TEMPORAL_MISMATCH           → no ConflictRecord
├── IDENTITY_UNRESOLVED         → no ConflictRecord
├── NON_COMPARABLE_PREDICATE    → no ConflictRecord
├── INSUFFICIENT_EVIDENCE       → no ConflictRecord
├── DECLARED_VS_OBSERVED_DRIFT  → ConflictRecord only when active policy drift is established
└── CONTRADICTION               → ConflictRecord when comparison dimensions are sufficiently aligned
```

## Finding boundary

A comparison or conflict is epistemic state. A Finding is a product-facing engineering problem.

Therefore:

```text
ComparisonRecord
→ maybe ConflictRecord
→ maybe Finding
```

not:

```text
any difference
→ Finding
```

Examples:

- runtime call violates an aligned architecture policy → active conflict → architecture-drift Finding candidate;
- two revisions disagree → revision mismatch only;
- same display name resolves to different entities → identity-resolution work, not dependency conflict;
- telemetry and semantic evidence corroborate each other → compatible comparison, potentially stronger confidence, no Finding.

## Invariants

1. Comparison does not erase either source assertion.
2. `comparison_class` describes relation between assertions, not global truth.
3. `conflict_state` is separate from comparison class.
4. No active contradiction before required dimensions are aligned.
5. Same names never prove identity.
6. Different environments, revisions, or non-overlapping valid-time windows are not contradictions by default.
7. Predicate-specific truth domains remain visible.
8. Conflict creation is append-only; it does not replace the ComparisonRecord.
9. Findings are downstream projections, not replacements for comparison/conflict evidence.
10. No global source-precedence rule is introduced by this model.

## Lab 13 role

Lab 13 should validate whether this boundary prevents false conflicts while preserving real drift and contradiction.

The schema is [`../schemas/comparison.schema.json`](../schemas/comparison.schema.json).
