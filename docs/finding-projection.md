# Finding projection boundary

## Thesis

> A Finding is a human/action-facing projection of an evidence-backed engineering problem. It is not a replacement for Assertions, Comparisons, or Conflicts.

The deterministic lineage is:

```text
Evidence
  ↓
Assertions
  ↓
ComparisonRecord
  ↓
optional ConflictRecord
  ↓
Finding candidate
```

Every downstream projection must preserve references to the upstream objects that justify it.

## Creation rule

A comparison may create a Finding candidate only when the comparison establishes an actionable problem.

Initial Lab 13 mapping:

```text
DECLARED_VS_OBSERVED_DRIFT + ACTIVE
→ ARCHITECTURE_DRIFT

CONTRADICTION + ACTIVE
→ EVIDENCE_CONFLICT
```

These do not create Findings by default:

```text
COMPATIBLE
NON_COMPARABLE_PREDICATE
IDENTITY_UNRESOLVED
SCOPE_MISMATCH
TEMPORAL_MISMATCH
REVISION_MISMATCH
ENVIRONMENT_MISMATCH
INSUFFICIENT_EVIDENCE
```

A mismatch may later contribute to another finding class, but only through an explicit rule with appropriate evidence. It must not become a generic problem merely because two records differ.

## Lineage invariant

A Finding projected from a ComparisonRecord must retain:

- every source `assertion_ref` required by the comparison;
- the originating `comparison_ref`;
- the `conflict_ref` when an active conflict exists;
- the union of relevant source `evidence_refs`;
- stable subject entity identity.

The source Assertions remain immutable. Creating, resolving, suppressing, or deleting a Finding does not rewrite historical evidence or assertions.

## Finding is not truth compression

Do not transform:

```text
Assertion A
Assertion B
Comparison C
Conflict D
```

into only:

```text
Finding F
```

and discard the upstream chain.

The Finding is reconstructable context for a human or workflow. The upstream records remain the epistemic substrate.

## Severity is not confidence

A finding may be high severity with weak evidence, or low severity with established evidence.

```text
severity   = consequence / urgency dimension
confidence = epistemic support dimension
```

They must remain independent.

## Verification before action

A deterministic Finding candidate is not execution authorization.

```text
Finding
→ verification
→ decision
→ authorization
→ action
```

This preserves the existing rule:

> Reasoning authority is not execution authority.

## Schema implication

`finding.schema.json` now supports optional `comparison_refs` so comparison lineage is first-class rather than hidden inside metadata.

This is a non-breaking extension. Existing Findings without a comparison source remain valid.

## Lab 13 guardrail

The offline harness verifies that:

1. active drift creates an `ARCHITECTURE_DRIFT` candidate;
2. active contradiction creates an `EVIDENCE_CONFLICT` candidate;
3. benign comparisons create no Finding candidate;
4. assertion, comparison, conflict, and evidence lineage is preserved;
5. source Assertions are not mutated;
6. missing source Assertions fail the lineage boundary.
