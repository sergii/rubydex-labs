# Canonical architecture map

This document is the canonical cross-model map for the evidence-backed engineering intelligence architecture.

It exists to prevent the individual domain models from drifting into overlapping semantics.

## System thesis

The system does not treat code, telemetry, architecture docs, Git history, or incidents as the system itself. They are sensors and evidence sources.

The durable substrate is an evidence-backed, temporal software world model that supports consequence analysis, investigation, decision-making, controlled action, and learning.

```text
SOFTWARE REALITY
      |
      v
SENSORS / SOURCES
      |
      v
EVIDENCE
      |
      v
IDENTITY RESOLUTION
      |
      v
ASSERTIONS
      |
      +-------------------+
      |                   |
      v                   v
CONFLICT / COMPARISON   CONFIDENCE / BELIEF
      |                   |
      +---------+---------+
                |
                v
          WORLD MODEL
                |
      +---------+---------+
      |                   |
      v                   v
     RISKS             FINDINGS
      |                   |
      +---------+---------+
                |
                v
            INCIDENT
                |
          HYPOTHESES
                |
          VERIFICATION
                |
            DECISION
                |
          AUTHORIZATION
                |
             ACTION
                |
                v
        OBSERVED REALITY
                |
      +---------+---------+
      |                   |
      v                   v
    IMPACT             RECOVERY
      |                   |
      +---------+---------+
                |
                v
           CALIBRATION
                |
                v
      ENGINEERING MEMORY
                |
                +---------------------> future planning / reasoning
```

The diagram is conceptual. Several layers interact iteratively rather than as a strict one-way pipeline.

## Canonical object boundaries

| Object | Question it answers | Owns | Must not own |
|---|---|---|---|
| Evidence | What did a sensor actually obtain? | immutable/append-only sensor output, provenance, scope, revision/time | interpretation, business consequence |
| Entity | What durable thing are observations about? | opaque stable identity, coarse entity type, lifecycle | mutable names as authoritative truth, arbitrary domain edges |
| IdentityLink | Do these representations refer to the same identity or identity lineage? | identity equivalence, rename/move lineage, representation mapping | ownership, capability/service architecture, generic business relationships |
| Assertion | What claim are we making about the world? | subject-predicate-object/value, provenance, temporal scope, assertion kind | alerting, operational workflow |
| ConfidenceRecord | What is the epistemic state behind a claim? | source strength, completeness, freshness, scope match, identity certainty, corroboration, contradictions, calibration | severity, priority |
| Conflict/Comparison | How do assertions relate after identity/scope/time alignment? | disagreement class, alignment dimensions, reconciliation outcome | silently choosing a winner |
| WorldModel | What does the current/historical evidence-backed software world look like? | materialized projections over entities/assertions/evidence | hidden facts not traceable to assertions |
| Risk | What harmful outcome is possible under current/proposed conditions? | conditions, likelihood, potential impact, predicted consequence, lifecycle | realized impact |
| Finding | Why should an engineer care now? | normalized actionable problem/risk projection, severity, affected scope, verification suggestions | raw evidence truth, execution authority |
| Hypothesis | What explanation are we testing? | causal/explanatory candidate, supporting/refuting evidence, investigation state | established root cause until earned |
| Verification | What evidence would discriminate or confirm/refute something? | question, hypothesis, evidence need, criteria, result | execution authority for remediation |
| Decision | Given what we knew then, what option was chosen and why? | alternatives, rationale, evidence context, decision maker | command execution result |
| Action | What state mutation was proposed/authorized/executed? | target, authorization state, execution state, reversibility, post-action evaluation links | belief that the problem is fixed |
| Incident | What operational case groups this evolving investigation? | timeline, membership, severity, impact state, root-cause state, coordination lifecycle | causal truth merely from membership/proximity |
| LearningRecord | What reusable lesson has been validated from history? | scoped, revisable learning, support/contradictions, applicability, freshness | raw event archive, universal truth without scope |

## Source-of-truth hierarchy is predicate-specific

There is no global rule such as `runtime > semantic > architecture`.

Examples:

- complete resolved code-reference set at revision X -> semantic backend;
- observed latency during window W -> telemetry;
- allowed dependency or declared owner -> architecture/policy source;
- what changed between revisions -> Git/change evidence;
- historical action effectiveness -> observed action + verification outcomes.

A source is authoritative only for the proposition it is designed to establish.

## Temporal model

Every important object should distinguish where applicable:

```text
valid time
= when something applied to the software world

recorded time
= when the evidence system learned or recorded it
```

Code may use revision identity in addition to wall-clock time. Runtime uses observation windows. Decisions must preserve the world state known at decision time. Predictions must remain separate from later observations.

## Projection rule

The product should not create separate truths for Operational, Overviewable, PR X-Ray, and Incident views.

They are projections over shared underlying objects.

```text
shared evidence / assertions / risks / findings
        |
        +--> PR X-Ray
        +--> Operational
        +--> Architecture/System view
        +--> Incident investigation
        +--> Agent interface
```

## Core invariants

1. Machines preserve facts; models interpret facts.
2. Evidence is immutable or append-only input.
3. Stable entity identity must not depend on mutable names.
4. Assertions, not graph edges, are the durable truth primitive.
5. Deterministic does not mean globally true; scope and revision still apply.
6. Unknown, conflicted, stale, and refuted are distinct belief states.
7. Severity and confidence are independent dimensions.
8. Prediction and observation must never be collapsed into one object.
9. Incident membership does not imply causality.
10. Execution success does not imply engineering outcome success.
11. Reasoning authority does not imply execution authority.
12. Historical memory can remain valid while current applicability becomes false.
13. Product projections may simplify presentation but must retain drill-down to evidence lineage.

## Primary lifecycle loops

### Evidence loop

```text
request
-> evidence plan
-> sensors
-> evidence
-> assertions
-> belief
-> answer / finding
```

### Investigation loop

```text
finding / incident
-> hypothesis
-> verification
-> evidence acquisition
-> assertion/confidence update
-> next hypothesis or decision
```

### Action loop

```text
risk/finding
-> decision
-> authorization
-> action
-> post-action verification
-> outcome
```

### Learning loop

```text
prediction / incident / action / outcome
-> candidate learning
-> validate scope and independence
-> learning record
-> future planner/reasoning
-> new evidence
-> reinforce/weaken/supersede
```

## Schema ownership map

Current schemas:

- `evidence-set.schema.json`
- `evidence-plan.schema.json`
- `entity.schema.json`
- `identity-link.schema.json`
- `assertion.schema.json`
- `confidence.schema.json`
- `conflict.schema.json`
- `risk.schema.json`
- `finding.schema.json`
- `hypothesis.schema.json`
- `verification.schema.json`
- `decision.schema.json`
- `action.schema.json`
- `incident.schema.json`
- `incident-event.schema.json`
- `learning-record.schema.json`

These contracts are research contracts, not yet a production persistence schema.

## Design principle for future additions

Before adding a new first-class object, ask:

1. Is this new truth, or just a projection of an existing object?
2. Does it have its own identity and lifecycle?
3. Does it own semantics that cannot safely live in an assertion?
4. Does keeping it separate preserve an important safety or epistemic boundary?
5. Can it be reconstructed from lower-level evidence without loss?

If the answer is mostly "projection", do not add another durable object.
