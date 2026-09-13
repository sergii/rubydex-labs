# Lab 12 — deterministic EvidenceSet preservation

> **Status: PLANNED — NOT RUN**
>
> This lab has not been designed or executed yet. Its protocol, corpus, ground truth, scoring, and workflow are intentionally deferred until Lab 11 has been run and interpreted.

## Research question

Can machine-owned `EvidenceSet` results eliminate completeness loss between deterministic evidence acquisition and the final answer?

## Motivation

Lab 10 showed a concrete failure mode: the semantic backend returned the complete correct set, but the model dropped an item while projecting the evidence into its final answer.

The proposed boundary is:

```text
deterministic backend
        |
        v
machine-owned EvidenceSet
        |
        +--> deterministic membership/count validation
        |
        v
model interpretation
```

The model may explain the set. It should not be responsible for reconstructing authoritative membership when completeness matters.

## Planned comparison

```text
A = raw tool output -> model reconstructs final set
B = tool output -> EvidenceSet -> model interprets
C = EvidenceSet -> deterministic set rendering + model explanation
```

## Planned metrics

- exact set recall;
- exact set precision;
- count agreement;
- provenance retention;
- completeness-guard violations;
- token/cost overhead.

## Dependency

Do not finalize or run this lab before interpreting Lab 11.

See [`../../docs/research-roadmap.md`](../../docs/research-roadmap.md) for the full sequence.
