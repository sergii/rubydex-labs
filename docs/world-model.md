# Evidence-backed software world model

This document defines the conceptual layer above evidence acquisition. It is a research model, not yet a production storage design.

## Core idea

The world model must not become another hand-maintained architecture graph that silently drifts away from reality.

Its durable primitive is not a node or an edge. It is an **evidence-backed assertion**.

```text
sensor observation
      |
      v
immutable evidence
      |
      v
assertion
      |
      v
materialized world model
      |
      v
reasoning / consequence / decision
```

A graph, architecture map, service catalog, X-Ray view, or incident timeline is a projection over assertions and evidence. It is not the ultimate source of truth.

## Why assertions come before the graph

A plain graph can say:

```text
Checkout -> calls -> PaymentGateway
```

but an engineering system also needs to know:

```text
who established this?
from which sensor?
at which code revision?
was it declared or observed?
is it complete?
when was it true?
is it still believed to be true?
what evidence supports it?
is there conflicting evidence?
```

Therefore a relationship without provenance is insufficient for the world model.

## Primitive layers

### Entity

An entity is a stable identity that can accumulate assertions over time.

Examples:

```text
Capability: Checkout
BusinessFlow: Checkout.PaymentCapture
Service: payments-api
Component: Payments::Gateway
Queue: payments
Database: primary-postgres
ExternalDependency: Stripe
Owner: payments-team
Policy: successful-capture-records-ledger
SLO: checkout-availability
Change: git:abc123
Deployment: deploy:2026-09-14-001
Incident: INC-92
```

Entity identity should survive display-name changes where possible.

### Evidence

Evidence is immutable or append-only sensor output with provenance.

Examples:

- a Rubydex resolved relationship set at Git revision `abc123`;
- an OpenTelemetry trace observed at time `T`;
- a Git diff;
- a test result;
- a declared architecture policy;
- an incident record.

Evidence is what a machine actually obtained. It should not be rewritten to match a later interpretation.

### Assertion

An assertion is a claim about the world backed by one or more evidence records.

Conceptually:

```text
subject
predicate
object/value
scope
valid time
observed/recorded time
provenance
confidence
status
supporting evidence
```

Examples:

```text
Payments::CaptureJob --depends_on--> Payments::Gateway
Checkout.PaymentCapture --owned_by--> payments-team
successful-capture --must_produce--> ledger-entry
payments-api --p95_latency--> 2.8s
PR-918 --changed--> Payments::Gateway
```

Assertions may be deterministic, declared, observed, inferred, predicted, or derived. Those categories must not be collapsed.

## Assertion kinds

At minimum the system should distinguish:

```text
DETERMINISTIC   established by a deterministic backend
DECLARED        explicitly stated architecture/policy/ownership
OBSERVED        measured at runtime or by execution
DERIVED         computed from other assertions/evidence
PREDICTED       forecast before observation
```

This distinction is essential. `Rubydex says A references B`, `architecture says A may depend on B`, and `OTEL observed A calling B` are different claims even if they render as a similar edge.

## Time model

The world model needs at least two notions of time:

```text
valid_at / valid_from / valid_to
    when the assertion applies to the software world

recorded_at
    when the evidence system learned or recorded it
```

For code evidence, Git revision may be more precise than wall-clock time. For runtime evidence, timestamp/window is primary. For architecture declarations, both revision and effective time may matter.

This lets the system answer both:

```text
What did we believe on Monday?
What was actually true for revision abc123?
```

without overwriting history.

## Conflicts are first-class

The world model must allow conflicting assertions.

Example:

```text
DECLARED:
checkout-service -> allowed_dependency -> payments-api

OBSERVED:
checkout-service -> calls -> legacy-payments-api
```

The correct behavior is not to choose one silently. The discrepancy is itself a finding:

```text
DECLARED != OBSERVED
        |
        v
architecture drift / policy risk
```

Likewise:

```text
SEMANTIC possible dependency
!=
RUNTIME observed dependency
```

is not necessarily a contradiction. One describes possibility; the other describes observation.

## World model as a materialized projection

The current world model can be materialized from active assertions:

```text
Evidence Store
     |
     v
Assertion Store
     |
     +---- current projection ----> system graph
     |
     +---- historical projection -> temporal graph
     |
     +---- PR projection ---------> X-Ray
     |
     +---- runtime projection ----> Operational
     |
     +---- incident projection ---> investigation view
```

This prevents each product surface from maintaining a separate version of reality.

## Consequences are not raw facts

A consequence such as:

> Customers may be charged while orders remain unconfirmed.

should not be stored as if it were a deterministic code fact.

It is a derived or predicted assertion backed by lower-level evidence:

```text
semantic evidence
+ architecture policy
+ runtime history
        |
        v
consequence assertion
```

It should carry confidence, rationale/provenance, and links to supporting evidence.

## Prediction and verification

The world model should make Lab 16 possible by representing predictions explicitly.

```text
PREDICTED assertion
    subject: proposed change
    predicate: may_increase
    object: checkout latency
    confidence: 0.72
    evidence: [...]

            deploy
              |
              v
OBSERVED assertion
    subject: checkout
    predicate: p95_latency
    value: ...

              |
              v
prediction evaluation
```

The prediction is never rewritten into an observation. The relationship between them records whether reality supported, contradicted, or remained inconclusive about the prediction.

## Confidence

Confidence must not become a decorative LLM number.

Where possible it should be derived from evidence properties such as:

- deterministic versus inferred source;
- evidence freshness;
- completeness;
- corroboration across independent sensors;
- contradictions;
- scope match;
- historical prediction calibration.

A deterministic complete Rubydex set can have strong confidence in set membership for a pinned revision while still saying nothing about runtime reachability or business importance.

## The resulting architecture

```text
                         ENGINEERING REQUEST
                                  |
                                  v
                         Evidence Planner
                                  |
                 +----------------+----------------+
                 |                |                |
                 v                v                v
              source          semantic          runtime
                Git            Rubydex           OTEL
                 |                |                |
                 +--------- architecture ----------+
                                  |
                                  v
                         immutable evidence
                                  |
                                  v
                         evidence-backed
                           assertions
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
             current world model         temporal history
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                          reasoning layer
                                  |
                                  v
                     consequence / prediction
                                  |
                                  v
                     verification / decision
                                  |
                                  v
                         observed reality
                                  |
                                  +---- feedback
```

## Important boundary

The world model is **not**:

- a giant prompt;
- a graph generated once by an LLM;
- a replacement for source code;
- a replacement for telemetry;
- an architecture wiki with AI summaries;
- a bag of embeddings.

It is a temporal, evidence-backed set of claims about the software system, with explicit provenance and truth-source semantics.

## Research implication

The Labs should continue to test the layers independently before building a generalized platform:

```text
Lab 11 -> can we plan evidence?
Lab 12 -> can we preserve authoritative evidence?
Lab 13 -> can we combine different truth sources?
Lab 14 -> can we add observed runtime truth?
Lab 15 -> can assertions remain correct across time/change?
Lab 16 -> can predictions be evaluated against later observations?
```

Only after those boundaries survive experiments should the repository attempt a concrete production storage or graph architecture.

## Working invariant

> Evidence is immutable input. Assertions are versioned claims. The world model is a projection. Consequences are derived. Predictions must eventually face observations.
