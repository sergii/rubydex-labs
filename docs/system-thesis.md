# System thesis

The Labs increasingly point beyond Rubydex-specific benchmarking toward a broader engineering evidence architecture.

## Working thesis

```text
Code is not the system.
Telemetry is not the system.
Architecture documentation is not the system.

They are sensors.

The durable product is the evolving,
evidence-backed model of the system.
```

A useful AI engineering system should not begin by loading as much repository context as possible. It should begin by asking what must be known, which evidence source can establish it, and how the resulting facts should be preserved before model reasoning begins.

## Sensor model

```text
SOURCE          -> files / AST / symbols / local navigation
SEMANTIC        -> Rubydex / semantic code graph
RUNTIME         -> OpenTelemetry / metrics / logs / traces
ARCHITECTURE    -> capabilities / flows / ownership / policy
CHANGE          -> Git / PR / deployment history
BEHAVIOR        -> tests / simulations / RunWitness-style verification
```

Each sensor answers a different class of question. None of them is the system model by itself.

## Evidence pipeline

```text
engineering request
        |
        v
what must be known?
        |
        v
Evidence Planner
        |
        v
which sensor can establish each fact?
        |
        v
machine-preserved evidence
        |
        v
model reasoning / evidence fusion
        |
        v
human-facing consequence
        |
        v
decision / verification / action
```

The architectural split is deliberate:

> Machines establish and preserve facts. Models connect and interpret facts. Humans act on consequences.

## Context versus evidence

Generic context is simply material supplied to a model. Evidence is stronger because it carries a claim boundary.

Useful evidence can include:

```text
source
scope
revision or timestamp
provenance
confidence
completeness
membership/count when set-valued
```

For example, `five production references exist at revision X` is not merely prompt context. It is a scoped assertion with provenance and completeness semantics.

## System knowledge

Implementation evidence alone does not establish business meaning.

A system model eventually needs entities such as:

```text
Capability
BusinessFlow
Service
Component
Data
Queue
Database
ExternalDependency
Infrastructure
Owner
Policy
SLO
Change
Incident
Risk
Consequence
Evidence
```

Classes, methods, constants, and files remain important, but they live below this layer as implementation evidence.

## Temporal dimension

A static graph answers `what exists?`.

An engineering world model must also answer:

```text
what existed before?
what changed?
when was it deployed?
what happened afterward?
has this happened before?
```

This requires evidence to be revision- and time-aware.

## Closed loop

The long-term target is not analysis-only tooling but a feedback loop:

```text
CHANGE
  |
  v
predict consequences
  |
  v
verify before deploy
  |
  v
deploy
  |
  v
observe reality
  |
  v
compare prediction with observation
  |
  v
update system knowledge
```

That loop is the bridge from code intelligence to engineering intelligence.

## Product projection

A single evidence-backed system model could support multiple human-facing projections:

```text
Operational view   -> what is broken or uncovered?
System view        -> how does the system work?
PR X-Ray           -> what can this change affect?
Incident view      -> what changed and why did this happen?
Agent interface    -> which evidence is needed for this question?
```

These should not require separate, contradictory world models. They can be projections over a shared evidence substrate.

## Current research path

Labs 01–10 established the progression from semantic indexing to evidence routing. Lab 11 is designed to test multi-backend evidence planning. Labs 12–16 are captured in [`research-roadmap.md`](research-roadmap.md), culminating in prediction-versus-observed-reality.

The research question has therefore evolved from:

> Does Rubydex help an AI coding agent?

into:

> What is the cheapest reliable evidence path for an engineering question, and can a system turn those facts into consequences that survive contact with reality?
