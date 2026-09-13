# Finding model

A Finding is the normalized engineering problem projected from evidence-backed assertions, conflicts, policies, risks, and observed behavior.

It is not an LLM summary and not merely an alert string.

## Core idea

```text
Evidence
  ↓
Assertions
  ↓
Conflicts / policy checks / anomaly rules
  ↓
Finding
  ↓
Impact / severity / verification / action
  ↓
Lifecycle
```

A Finding is where the internal world model becomes useful to a human or automation.

## What a Finding answers

A useful Finding should answer:

```text
What happened or may happen?
Why do we believe this?
What is affected?
How bad could it be?
How certain are we?
What should be checked next?
Who owns the affected surface?
Is this new, recurring, acknowledged, resolved, or regressed?
```

## Finding versus assertion

An assertion is a claim about the software world.

```text
checkout-service --calls--> legacy-payments
```

A Finding is an engineering interpretation of one or more claims.

```text
Architecture drift: checkout is calling legacy-payments despite the declared payments-v2 boundary.
```

The Finding must retain references to the assertions and evidence that justify it.

## Finding versus conflict

A conflict is a disagreement between aligned assertions.

A Finding is created only when that disagreement is engineering-significant.

Examples:

```text
Conflict:
DECLARED checkout -> payments-v2
OBSERVED checkout -> legacy-payments

Finding:
ARCHITECTURE_DRIFT
```

A harmless scope mismatch may remain a conflict record without becoming a Finding.

## Finding classes

Initial taxonomy:

```text
ARCHITECTURE_DRIFT
POLICY_VIOLATION
IDENTITY_AMBIGUITY
STALE_KNOWLEDGE
COVERAGE_GAP
RUNTIME_ANOMALY
DEPENDENCY_RISK
CHANGE_RISK
DATA_INTEGRITY_RISK
RELIABILITY_RISK
PERFORMANCE_RISK
SECURITY_RISK
OWNERSHIP_GAP
PREDICTION_MISS
EVIDENCE_CONFLICT
UNKNOWN_RISK
```

The taxonomy should remain extensible. Product views may group these differently.

## Finding structure

Conceptually:

```text
id
class
title
summary
status
severity
confidence_record
subject_entity_refs
affected_entity_refs
assertion_refs
conflict_refs
evidence_refs
policy_refs
change_refs
incident_refs
impact
blast_radius
verification
suggested_actions
owner_refs
first_seen_at
last_seen_at
resolved_at
fingerprint
```

## Severity is not confidence

Severity answers:

> If this Finding is true, how consequential is it?

Confidence answers:

> How strongly does evidence support the Finding?

Therefore these combinations are valid:

```text
CRITICAL severity + TENTATIVE confidence
LOW severity + ESTABLISHED confidence
```

A high-risk but weakly-supported hypothesis may deserve urgent verification without being presented as fact.

## Severity model

Start with a simple ordered scale:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Severity should be derived from impact dimensions rather than directly guessed where possible.

Possible impact dimensions:

```text
customer impact
financial impact
data integrity
availability
security
regulatory/compliance
blast radius
recoverability
time sensitivity
```

The exact severity algorithm remains experimental.

## Blast radius

Blast radius should be explicit and structured.

Useful dimensions include:

```text
accounts/users affected
requests/jobs affected
capabilities/flows affected
services/components affected
regions/environments affected
data sets affected
financial exposure
percentage versus absolute count
```

This allows the same Finding class to be prioritized differently depending on actual reach.

## Impact

Impact should describe human/system consequence, not just implementation detail.

Weak:

```text
Payments::CaptureJob no longer invokes after_capture.
```

Stronger:

```text
Successful captures may no longer produce a ledger entry or order confirmation.
```

The first is evidence. The second is consequence.

## Verification

A Finding should carry concrete verification steps.

Example:

```text
- confirm whether successful provider captures are missing ledger records
- compare order confirmation rate before and after deploy
- inspect recent payment traces for synchronous capture path
```

Verification is distinct from remediation.

## Suggested actions

Suggested actions may include:

```text
investigate
collect_more_evidence
rollback
revert_change
add_monitoring
update_architecture_declaration
fix_identity_mapping
repair_policy_violation
contact_owner
acknowledge
suppress
```

The system should distinguish a recommendation from an automatic action.

## Lifecycle

A Finding should be durable over repeated observations.

Suggested statuses:

```text
OPEN
ACKNOWLEDGED
INVESTIGATING
MITIGATED
RESOLVED
SUPPRESSED
FALSE_POSITIVE
STALE
REGRESSED
```

Transitions should preserve history rather than overwriting prior state.

## Fingerprinting and deduplication

Repeated evidence should update the same Finding when it represents the same underlying problem.

A fingerprint may depend on:

```text
finding class
primary subject identity
relevant predicate/policy
scope/environment
important affected identities
```

It should not depend on mutable prose such as title text.

A recurrence after resolution should normally reopen as `REGRESSED` or create a linked recurrence, not silently create unrelated duplicate Findings.

## Evidence-driven state changes

Finding lifecycle should react to evidence.

Example:

```text
OPEN
  ↓ additional runtime evidence
INVESTIGATING
  ↓ deployment fixes observed drift
MITIGATED
  ↓ sufficient verification window
RESOLVED
```

If contradictory evidence later appears:

```text
RESOLVED
  ↓ problem observed again
REGRESSED
```

## Finding generation

Findings may originate from several mechanisms:

```text
conflict detector
policy evaluator
runtime anomaly detector
change-risk analysis
coverage analysis
prediction evaluation
human assertion
```

Regardless of origin, they should share the same normalized contract.

## Product projections

The same Finding can appear differently depending on product surface.

```text
Operational
  -> alert / incident risk / coverage gap

Overviewable
  -> system-map warning / ownership or architecture drift

PR X-Ray
  -> predicted change risk

Incident view
  -> active diagnostic hypothesis
```

The underlying Finding identity and evidence remain shared.

## Important invariants

1. A Finding must reference the assertions/evidence that justify it.
2. Severity and confidence are different dimensions.
3. A Finding may be severe even when confidence is low; the UI must communicate both.
4. Findings should be deduplicated by stable identity/fingerprint, not prose.
5. Findings preserve lifecycle history.
6. Verification steps are separate from remediation steps.
7. A conflict becomes a Finding only when the discrepancy is engineering-significant.
8. User-facing summaries may be model-generated, but Finding identity, evidence links, lifecycle, and machine-known impact fields must not depend on prose generation.
9. Resolved Findings may regress; history must remain queryable.
10. Automatic action requires a separate policy/authorization layer.

## Working thesis

> Evidence establishes facts. Assertions model beliefs. Conflicts expose disagreement. Findings turn meaningful disagreement, risk, or anomaly into an actionable engineering object.
