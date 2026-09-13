# Research roadmap

This document captures the next experimental sequence after Labs 01–11.

The repository has moved from asking whether semantic code intelligence is useful to a broader question:

> Can an engineering system build reliable, evidence-backed decisions by selecting, preserving, fusing, and validating the right evidence sources?

The working architecture is:

```text
engineering request
        |
        v
 Evidence Planner
        |
        v
 Evidence Plan
   /       |        |        \
source  semantic  runtime  architecture
   \       |        |        /
      machine-owned evidence
             |
             v
         reasoning
             |
             v
       consequence model
             |
             v
     verification / action
             |
             v
        observed reality
             |
             +---- feedback ---->
```

The key research sequence is intentionally cumulative. Each lab should establish one missing capability before the next lab adds another source of uncertainty.

## Lab 11 — Multi-backend evidence planner

**Status: DESIGNED — NOT RUN**

Question:

> Can a low-cost planner map one natural-language engineering request to the minimal reliable multi-backend `EvidencePlan`?

Scope:

- planning only;
- no downstream source traversal;
- no Rubydex execution;
- no runtime backend execution;
- no architecture backend execution.

This lab is already designed under `labs/11-evidence-planner/` and is protected by the global real-API spend kill switch.

## Lab 12 — Deterministic EvidenceSet preservation

**Status: PLANNED — NOT DESIGNED — NOT RUN**

Question:

> Can machine-owned `EvidenceSet` results eliminate completeness loss between deterministic evidence acquisition and the final answer?

Motivation:

Lab 10 produced one important failure: Rubydex returned the complete correct production-reference set, but the model dropped one item while summarizing it. The failure was not evidence acquisition. It was evidence projection.

Hypothesis:

For queries containing completeness semantics such as `all`, `every`, `complete`, or an equivalent requirement, membership, count, filtering, and provenance should remain machine-owned until after the user-visible result has been validated.

Proposed conditions:

```text
A = raw semantic tool output -> model reconstructs final set
B = semantic tool output -> deterministic EvidenceSet -> model interprets set
C = EvidenceSet -> deterministic final set rendering + model explanation
```

Primary metrics:

- exact set recall;
- exact set precision;
- count agreement;
- provenance retention;
- completeness-guard violations;
- token/cost overhead.

Success criterion:

The system must never emit an authoritative set whose membership count disagrees with the machine-owned EvidenceSet.

## Lab 13 — Evidence fusion

**Status: PLANNED — NOT DESIGNED — NOT RUN**

Question:

> Does combining semantic evidence with architecture knowledge improve consequence reasoning beyond either source alone?

Proposed evidence conditions:

```text
S  = semantic only
A  = architecture knowledge only
SA = semantic + architecture knowledge
```

Possible task:

A payment-flow change where semantic evidence establishes implementation reachability while architecture knowledge establishes policy, ownership, and business consequence.

Primary metrics:

- impacted capability/flow recall;
- policy violation recall;
- risk precision;
- verification-plan quality;
- unsupported-claim rate.

Expected lesson:

Semantic evidence answers `what is structurally connected?`; architecture evidence answers `what does that connection mean?`.

## Lab 14 — Runtime evidence backend

**Status: PLANNED — NOT DESIGNED — NOT RUN**

Question:

> Can the evidence planner add runtime observations when a correct answer depends on actual system behavior rather than code structure?

Candidate backend:

- OpenTelemetry traces;
- metrics;
- logs;
- synthetic runtime fixture if production-like telemetry is unavailable.

Representative questions:

- Did this change increase p95 latency?
- Which downstream dependency is actually slow?
- Are retries occurring in production?
- Which execution path is observed, not merely possible?

Important boundary:

Code evidence describes possible structure. Runtime evidence describes observed behavior.

Primary metrics:

- runtime route selection;
- evidence freshness correctness;
- observed-vs-inferred distinction;
- unsupported runtime claims;
- planner cost.

## Lab 15 — Temporal evidence and engineering memory

**Status: PLANNED — NOT DESIGNED — NOT RUN**

Question:

> Can the system reason over what changed, what existed before, and what happened after the change?

Evidence sources:

- Git commits / PRs;
- deploy events;
- incidents;
- runtime observations;
- system knowledge snapshots.

Target model:

```text
change
  -> affected system entities
  -> deployment
  -> observations
  -> incident / non-incident
```

Representative questions:

- What changed immediately before this regression?
- Have similar boundary changes caused incidents before?
- Which architecture relationships appeared or disappeared over time?

Primary metrics:

- causal candidate recall;
- temporal ordering accuracy;
- stale-evidence rate;
- revision/provenance correctness.

## Lab 16 — Prediction versus observed reality

**Status: PLANNED — NOT DESIGNED — NOT RUN**

Question:

> Can the system predict a meaningful engineering consequence before a change is deployed, then compare that prediction with observed runtime evidence afterward?

This is the first lab that closes the loop.

```text
proposed change
      |
      v
pre-deploy evidence plan
      |
      v
predicted consequences
      |
      v
verification / deploy
      |
      v
runtime observations
      |
      v
prediction-vs-reality comparison
```

Primary metrics:

- predicted consequence precision/recall;
- missed consequences;
- false alarms;
- confidence calibration;
- time-to-detection;
- whether new observations should update system knowledge.

A strong result here would move the project from code intelligence toward an evidence-backed engineering intelligence system.

## Research invariants

The following rules should survive individual experiments:

1. **Machines preserve facts. Models interpret facts.**
2. Complete sets remain machine-owned when a deterministic backend can preserve them.
3. Evidence has provenance, scope, revision/time, and confidence/completeness metadata where applicable.
4. Source, semantic, runtime, architecture, change, and behavioral evidence are different truth sources; do not collapse them into one generic context bucket.
5. Route or plan evidence before expensive reasoning where possible.
6. Do not attribute a result to a tool unless the tool was actually used and its evidence was consumed.
7. Separate possible structure from observed runtime behavior.
8. Separate implementation facts from human-facing consequences.
9. API-spending experiments remain disabled unless explicitly authorized by `RUN_WITH_REAL_OPENAI_API=true`.

## Long-term product hypothesis

The durable product is not a code browser, a telemetry dashboard, or an architecture wiki in isolation.

It is an evolving, evidence-backed model of the software system that can answer:

```text
What exists?
How is it connected?
What does it mean?
What changed?
What is happening now?
What could this change affect?
What actually happened afterward?
What should we do next?
```

Rubydex is one semantic sensor in that system. Runtime observability, Git/change history, tests, architecture knowledge, and policy are additional sensors.

The product layer is the fusion of those evidence sources into reliable engineering consequences and decisions.
