# Architecture design review

Status: active review before Labs 12–16 implementation.

This review checks whether the current evidence/world-model contracts have clear ownership boundaries or whether conceptual overlap is starting to accumulate.

## Executive conclusion

The architecture is coherent enough to proceed with Labs 12–16, but three cleanup areas should be resolved before treating the schemas as stable external contracts:

1. entity names/aliases are currently more authoritative than the identity thesis allows;
2. identity links currently contain ordinary architecture/domain relations;
3. conflict classification currently mixes true contradictions with benign comparison outcomes.

These are model-boundary issues, not reasons to redesign the whole architecture.

## 1. Entity names and aliases

### Current shape

`entity.schema.json` requires `canonical_name` and allows embedded `aliases` with temporal/source metadata.

### Problem

The identity thesis says names are observations and stable identity should survive mutable names. If mutable names and aliases live directly inside the durable Entity object, consumers may treat them as authoritative entity truth rather than evidence-backed projections.

This creates two competing ways to represent names:

```text
Entity.aliases
vs
assertions / evidence-backed identity observations
```

### Recommended direction

Keep Entity minimal:

```text
id
entity_type
lifecycle/status
recorded_at
minimal metadata
```

Treat names as projection data derived from evidence-backed assertions or representation mappings.

A future schema revision should either:

- make `canonical_name` an explicitly non-authoritative display projection; or
- remove mutable naming from the core entity record and derive it from assertions/representation records.

Do not break schema v1 solely for this cleanup until a concrete storage/query path is being built.

## 2. IdentityLink contains domain relations

### Current shape

The IdentityLink relation enum includes:

```text
SAME_AS
RENAMED_FROM
MOVED_FROM
REPRESENTS
OBSERVED_AS
IMPLEMENTED_BY
DEPLOYED_AS
OWNED_BY
SERVES_CAPABILITY
DERIVED_FROM
```

### Problem

Several of these are not identity-resolution relations.

For example:

```text
payments-api OWNED_BY payments-team
payments-api SERVES_CAPABILITY PaymentCapture
```

These are ordinary world-model assertions. Putting them in IdentityLink creates two graph systems:

```text
IdentityLink edges
Assertion edges
```

and makes it unclear where architecture/domain truth belongs.

### Recommended boundary

IdentityLink should be reserved for identity/representation continuity.

Strong candidates to remain:

```text
SAME_AS
RENAMED_FROM
MOVED_FROM
REPRESENTS
OBSERVED_AS
```

`DEPLOYED_AS` may remain if used specifically as representation resolution between a logical entity and a deployment representation, but it should be reviewed carefully.

Move these to ordinary assertions:

```text
IMPLEMENTED_BY
OWNED_BY
SERVES_CAPABILITY
DERIVED_FROM
```

Potentially also `DEPLOYED_AS` if it is being used as architecture truth rather than identity mapping.

### Migration principle

Do not destructive-convert historical links. A future migration should create assertions with provenance and supersede/retract the old identity links.

## 3. Conflict versus comparison

### Current shape

`conflict.schema.json` calls the field `conflict_class`, but includes:

```text
NON_CONFLICTING_DIFFERENCE
SCOPE_MISMATCH
TEMPORAL_MISMATCH
```

### Problem

These are useful comparison outcomes but are not necessarily conflicts.

Calling all of them conflicts may cause downstream logic to inflate disagreement into a problem or Finding.

### Recommended direction

Conceptually rename the layer to comparison/reconciliation:

```text
AssertionComparison
```

with a classification such as:

```text
COMPATIBLE_DIFFERENCE
SCOPE_MISMATCH
TEMPORAL_MISMATCH
DECLARED_VS_OBSERVED_DRIFT
DETERMINISTIC_CONTRADICTION
OBSERVATION_CONTRADICTION
IDENTITY_CONFLICT
POLICY_CONFLICT
DERIVATION_CONFLICT
PREDICTION_MISS
```

Then add a derived boolean/state:

```text
conflict_state:
  NONE
  EXPLAINED
  ACTIVE
  RESOLVED
```

This preserves the important rule:

> compare first; call it a conflict only after identity, scope, time, and predicate semantics have been aligned.

Again, schema v1 can remain as-is until an implementation depends on it.

## 4. Confidence placement

Current design is largely correct: confidence is structured and belongs to assertions, identity resolution, findings, predictions, and learnings according to their own epistemic state.

Avoid creating one global confidence value on the WorldModel or Entity.

Confidence is proposition-specific.

## 5. Risk versus Finding

Boundary is sound if kept strict:

```text
Risk = possible harmful outcome under conditions
Finding = product-facing actionable interpretation/problem state
```

A Finding may reference one or more risks, but should not duplicate full risk semantics.

Do not turn every Risk into a Finding automatically. Policy, severity, confidence, exposure, novelty, and user relevance should control projection.

## 6. Finding versus Incident

Boundary is sound:

- Finding is a durable problem/risk state.
- Incident is a coordinated temporal case/investigation.

Multiple Findings can belong to one Incident; a Finding can exist without an Incident.

Incident membership must not create causal assertions.

## 7. Hypothesis versus predicted assertion

Potential overlap exists.

A `PREDICTED` assertion represents a forecast about the world.

A Hypothesis represents an investigation explanation under test.

Example:

```text
PREDICTED assertion:
PR-918 may increase duplicate capture probability.

Hypothesis:
PR-918 caused the currently observed duplicate captures.
```

Keep them separate because they differ in temporal role, lifecycle, and evaluation semantics.

## 8. Verification versus EvidencePlan

These should also remain separate:

```text
Verification
= epistemic question + pass/fail/inconclusive criteria

EvidencePlan
= acquisition plan for collecting evidence needed to answer the question
```

One Verification can produce one or multiple EvidencePlans over time as uncertainty changes.

## 9. Decision versus Action

Boundary is essential for safety.

```text
Decision
= selected option and rationale given evidence at time T

Action
= proposed/authorized/executed state mutation
```

Never infer execution authority from a decision record.

## 10. IncidentEvent versus generic event stream

The current IncidentEvent schema is useful as an incident projection, but should not become the universal event-store primitive by accident.

A future generic event stream may exist beneath it, but it is not required for Labs 12–16.

Do not add one prematurely.

## 11. LearningRecord versus Assertion

A LearningRecord should not become another generic claim type.

Its special semantics justify a separate object only when it contains:

- repeated historical support/contradiction;
- applicability rules;
- calibration/decay;
- reinforcement/weakening lifecycle;
- influence on future routing/reasoning.

A one-off factual lesson should remain an Assertion, not a LearningRecord.

## 12. Missing but intentionally deferred objects

The following concepts do not need first-class schemas yet:

### Alert

A delivery event triggered by a Finding/Incident transition. It can remain product/integration-level until notification semantics are being implemented.

### Recommendation

Can initially remain a projection attached to Findings/Decisions. Add a durable object only if recommendations need their own lifecycle/evaluation history.

### Authorization

Conceptually separate and safety-critical, but a dedicated schema is not mandatory until guarded execution is implemented. Action may reference policy/approval records in the meantime.

### Outcome

Action outcome and prediction evaluation can initially be represented via Action/Verification/Assertion links. Add a dedicated object only if cross-action outcome analysis requires stable identity/lifecycle.

## 13. Schema stability tiers

Before implementation, treat schemas in three tiers.

### Tier A — closest to stable conceptual core

```text
EvidencePlan
EvidenceSet
Assertion
ConfidenceRecord
```

### Tier B — stable idea, boundary cleanup likely

```text
Entity
IdentityLink
Conflict/Comparison
Risk
Finding
```

### Tier C — workflow/product semantics still exploratory

```text
Hypothesis
Verification
Decision
Action
Incident
IncidentEvent
LearningRecord
```

Do not publish Tier B/C schemas as external compatibility promises yet.

## 14. What Labs 12–16 should validate

### Lab 12 — EvidenceSet preservation

Validate machine-owned completeness, membership, counts, provenance, and deterministic rendering.

### Lab 13 — Evidence fusion

Validate cross-source assertion fusion, identity prerequisites, corroboration, contradiction, and comparison semantics.

This lab should directly stress the IdentityLink and Conflict/Comparison boundaries identified above.

### Lab 14 — Runtime evidence

Validate observed assertion semantics, observation windows, freshness, completeness limits, and runtime identity mapping.

### Lab 15 — Temporal evidence

Validate valid-time versus recorded-time, revisions, stale/current projections, rename/move continuity, and architecture epochs.

This lab should directly stress the Entity naming/alias cleanup area.

### Lab 16 — Prediction versus reality

Validate PREDICTED versus OBSERVED assertions, risk materialization, realized impact, calibration, and learning updates.

## 15. Stop rule for abstraction

No new durable domain object should be added before Lab 13 unless one of these is true:

1. an existing schema cannot represent required evidence without information loss;
2. safety requires a separate authorization/lifecycle boundary;
3. the object has durable identity and independent lifecycle;
4. two existing objects are being overloaded with incompatible semantics.

Otherwise prefer assertions, references, or projections.

## Current recommendation

Proceed with Labs 12–16 using the current research schemas, but treat the three identified cleanup items as explicit hypotheses to validate rather than immediately performing breaking migrations.

The next engineering work should therefore move back from ontology expansion to executable research, beginning with Lab 12 offline harness design and deterministic EvidenceSet rendering.
