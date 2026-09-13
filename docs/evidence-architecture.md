# Evidence architecture

This document freezes the architectural lessons from Labs 06–10.

The central question is not whether an agent should always use Rubydex. It is:

> What is the cheapest reliable evidence path for an engineering question?

Rubydex is one evidence backend among several. Source text, semantic structure, runtime observations, and explicit architecture knowledge answer different classes of questions.

## Core principle

```text
Models may interpret evidence.
Models must not reconstruct authoritative complete sets
when a deterministic backend can preserve them.
```

A model is useful for synthesis, consequence reasoning, prioritization, and explanation. It is a weak place to preserve completeness-sensitive facts such as every resolved reference, every descendant, or every item in a filtered machine result.

## Evidence classes

The current taxonomy is:

- `SOURCE_LOCAL` — a local declaration, file, method, or nearby source fact.
- `SEMANTIC_RELATIONSHIP_SET` — a complete resolved repository-wide relationship set such as descendants, references, reopenings, extensions, callers/users, or a structural impact neighborhood.
- `RUNTIME_BEHAVIOR` — observed execution evidence such as traces, metrics, logs, latency, retries, errors, query counts, or production behavior.
- `ARCHITECTURE_KNOWLEDGE` — declared ownership, business capabilities and flows, architectural boundaries, policies, intended dependencies, and other system knowledge that code structure alone cannot establish.

These classes are about the primary truth source, not the UI shown to a human.

## EvidenceRoute

An `EvidenceRoute` selects the backend that can establish a fact reliably.

```text
SOURCE_LOCAL                -> source / AST / local navigation
SEMANTIC_RELATIONSHIP_SET   -> Rubydex or another semantic index
RUNTIME_BEHAVIOR            -> OpenTelemetry / logs / metrics / traces
ARCHITECTURE_KNOWLEDGE      -> architecture knowledge / ontology / policy store
```

Routing should happen before expensive reasoning whenever possible.

Lab 09 showed that an explicit task-shape route could outperform leaving tool selection to the agent. Lab 10 showed that a small natural-language classifier could recover the frozen oracle route cheaply.

## EvidenceSet

An `EvidenceSet` is a machine-preserved result whose membership matters.

Typical examples:

- every direct reference to a constant;
- every named descendant;
- every production implementation of an interface;
- all traces matching an incident predicate;
- all policies applicable to a component.

For completeness-sensitive tasks, the backend and deterministic filter layer own:

- membership;
- filtering;
- count;
- provenance;
- completeness status.

The model may summarize or interpret the set, but it should not manually recreate it from a longer tool response.

```text
backend
   |
   v
raw machine result
   |
   v
deterministic filter
   |
   v
EvidenceSet
   |
   +--> count / membership / provenance remain authoritative
   |
   v
model reasoning
```

The schema is defined in [`../schemas/evidence-set.schema.json`](../schemas/evidence-set.schema.json).

### Required invariants

JSON Schema alone cannot express every semantic invariant, so implementations must additionally validate:

1. `count == items.length`.
2. If `complete == true`, pagination/truncation must have been exhausted or explicitly ruled out by the backend.
3. `scope` and filters must be recorded rather than silently applied.
4. Every item must be traceable to `provenance` and the pinned repository/runtime revision where applicable.
5. Model-generated additions must never silently enter an authoritative `EvidenceSet`.

## EvidencePlan

A real engineering request often needs more than one evidence class.

For example:

> Is this checkout change safe in production, what does it affect, and does it violate any boundary?

may require:

```text
SEMANTIC_RELATIONSHIP_SET   required
ARCHITECTURE_KNOWLEDGE      required
RUNTIME_BEHAVIOR            required
SOURCE_LOCAL                optional
```

That is not a single-label routing problem. It is an evidence-planning problem.

An `EvidencePlan` is a small DAG of evidence steps. Each step records:

- evidence class;
- backend;
- required versus optional status;
- purpose;
- dependencies on earlier steps;
- optional backend query hints.

The schema is defined in [`../schemas/evidence-plan.schema.json`](../schemas/evidence-plan.schema.json).

Example:

```json
{
  "schema_version": "1",
  "request": "Is this checkout change safe in production?",
  "steps": [
    {
      "id": "semantic-impact",
      "evidence_class": "SEMANTIC_RELATIONSHIP_SET",
      "backend": "rubydex",
      "requirement": "required",
      "purpose": "Establish the resolved structural impact set.",
      "depends_on": []
    },
    {
      "id": "architecture-policy",
      "evidence_class": "ARCHITECTURE_KNOWLEDGE",
      "backend": "architecture_knowledge",
      "requirement": "required",
      "purpose": "Check declared boundaries and policies.",
      "depends_on": []
    },
    {
      "id": "runtime-evidence",
      "evidence_class": "RUNTIME_BEHAVIOR",
      "backend": "otel",
      "requirement": "required",
      "purpose": "Check observed production behavior and recent regressions.",
      "depends_on": ["semantic-impact"]
    }
  ]
}
```

## Product-shaped pipeline

The architecture suggested by the experiments is:

```text
                  Engineering request
                          |
                          v
                   Evidence Planner
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       source          semantic          runtime
     / AST / Git        Rubydex          OTEL
          \               |               /
           +--------------+--------------+
                          |
                          v
                 machine-owned evidence
                          |
                          +------ architecture / policy
                          |
                          v
                       Reasoner
                          |
                          v
                consequence / X-Ray
```

The human-facing layer should emphasize consequences, risks, affected capabilities, verification, and policy—not raw implementation unless the user drills down.

## What remains experimental

The schemas in this repository are architecture contracts, not a claim that the planner is production-ready.

Open questions include:

- multi-label planning accuracy on ambiguous natural-language requests;
- when evidence steps can run in parallel;
- confidence and escalation thresholds;
- caching and freshness policies;
- reconciliation between source, semantic, runtime, and declared architecture facts;
- backend failure behavior;
- how to preserve evidence identity across time and code revisions.

The next experiments should evolve from `request -> one class` toward `request -> EvidencePlan`, while keeping each backend deterministic where it can be deterministic.
