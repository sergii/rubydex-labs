# Lab 12 — deterministic EvidenceSet preservation

> **Status: DESIGNED — NOT RUN**
>
> This lab is fully designed but intentionally not executed. Real OpenAI API execution remains disabled unless the repository's explicit API-spend authorization conditions are satisfied and the user explicitly authorizes a new run.

## Research question

Can a machine-owned `EvidenceSet` boundary eliminate completeness loss between deterministic evidence acquisition and the final human-facing answer?

## Motivation

Lab 10 exposed a precise failure mode: the semantic backend returned the complete correct set, but the model dropped one item while projecting the evidence into its final answer.

The correct boundary is:

```text
deterministic backend
        |
        v
machine-owned EvidenceSet
        |
        +--> deterministic schema / count / membership validation
        |
        +--> deterministic authoritative rendering
        |
        v
model interpretation / explanation
```

The model may explain the set. It must not be responsible for reconstructing authoritative membership when completeness matters.

## Core invariant

> If membership is machine-known, final authoritative membership must remain machine-rendered.

The model can add explanation beside the authoritative set, but may not add, remove, reorder for semantic effect, deduplicate by intuition, or rewrite authoritative members into a new list that becomes the source of truth.

## Experimental conditions

### A — reconstruction baseline

```text
raw deterministic backend output
        ↓
model
        ↓
model reconstructs membership + explanation
```

This reproduces the unsafe boundary seen in Lab 10.

### B — preserved EvidenceSet, model renders

```text
raw backend output
        ↓
deterministic EvidenceSet builder
        ↓
validation
        ↓
model receives complete EvidenceSet
        ↓
model renders membership + explanation
```

This tests whether merely giving the model a normalized complete set is sufficient.

### C — preserved EvidenceSet, deterministic authoritative rendering

```text
raw backend output
        ↓
deterministic EvidenceSet builder
        ↓
validation
        ↓
┌──────────────────────────────────┐
│ authoritative set renderer       │  machine-owned
└──────────────────────────────────┘
        +
┌──────────────────────────────────┐
│ model explanation                │  non-authoritative
└──────────────────────────────────┘
```

Condition C is the proposed production architecture.

## Offline design corpus

The initial corpus is deliberately small and adversarial. It tests preservation properties rather than model intelligence.

Fixture classes:

1. `production-references-5` — reproduces the Lab 10 shape: five authoritative members where dropping one changes correctness.
2. `empty-complete-set` — count 0, `complete=true`; must render an explicit empty result rather than invent uncertainty.
3. `incomplete-set` — `complete=false`; renderer must not claim "all" or "none".
4. `duplicate-looking-members` — two members with similar labels but distinct stable keys; no intuitive deduplication.
5. `same-symbol-different-path` — membership identity is not display text alone.
6. `provenance-sensitive` — every member and the set-level backend/revision must remain traceable.
7. `large-set` — enough members to expose accidental truncation and count drift.
8. `filtered-set` — include/exclude/filter scope must be surfaced so membership is not interpreted globally.

The fixtures are synthetic but mirror the exact failure class observed in Lab 10. No live backend or API call is required for offline validation.

## Machine-owned invariants

For every `EvidenceSet`:

1. `count == items.length`.
2. item `key` values are unique.
3. the renderer outputs exactly the stored item keys, no more and no fewer.
4. `complete=true` is required before wording that implies exhaustive membership (`all`, `every`, `none`, `only these`).
5. `complete=false` must surface an incompleteness marker.
6. set-level provenance is rendered or attached losslessly.
7. scope/filter metadata is preserved.
8. deterministic rendering is stable for identical normalized input.
9. model explanation cannot mutate authoritative membership.
10. authoritative-set validation failure is fail-closed: no completeness claim is emitted.

## Metrics

Primary:

- exact membership recall;
- exact membership precision;
- exact count agreement;
- unauthorized addition count;
- unauthorized omission count;
- completeness-claim correctness;
- provenance retention;
- scope retention.

Secondary, only if/when model conditions are later authorized:

- explanation usefulness;
- latency;
- tokens;
- cost.

The primary offline harness does not require an LLM.

## Scoring

For an expected key set `G` and rendered authoritative key set `R`:

```text
recall    = |G ∩ R| / |G|        (1.0 when both are empty)
precision = |G ∩ R| / |R|        (1.0 when both are empty)
exact     = G == R
count_ok  = rendered_count == |G|
```

Completeness correctness is scored independently because a perfectly copied incomplete set must still not be described as exhaustive.

A sample passes the deterministic boundary only when:

```text
exact_membership
AND count_ok
AND provenance_ok
AND scope_ok
AND completeness_claim_ok
```

## Expected hypothesis

Expected ordering:

```text
C > B > A
```

for completeness-sensitive outputs.

More importantly, condition C changes the failure mode from probabilistic transcription to deterministic validation. If C fails, the bug should be in code/schema/fixture handling rather than stochastic model output.

## Production implication

Human-facing answers should become composite objects:

```text
Answer
├── authoritative_facts   # deterministic rendering from EvidenceSet
└── explanation           # model-generated interpretation
```

The UI/API must preserve which section is authoritative.

## Files

- `fixtures/evidence-sets.json` — frozen offline corpus.
- `scripts/validate-evidence-set.py` — invariant validator.
- `scripts/render-evidence-set.py` — deterministic authoritative renderer.
- `scripts/score-rendering.py` — exact preservation scorer.
- `STATUS.md` — execution state and safety boundary.

## Relationship to later labs

Lab 12 establishes fact preservation. It intentionally does not solve evidence fusion.

```text
Lab 12: preserve one machine-owned evidence set
Lab 13: combine multiple evidence/assertion sources without semantic collapse
Lab 14: add runtime evidence semantics
Lab 15: preserve temporal validity
Lab 16: compare prediction with observed reality
```

## Stop condition

Do not add model complexity to repair deterministic preservation failures. If membership is already known, fix the machine boundary first.

See [`../../docs/evidence-architecture.md`](../../docs/evidence-architecture.md), [`../../schemas/evidence-set.schema.json`](../../schemas/evidence-set.schema.json), and [`../../docs/research-roadmap.md`](../../docs/research-roadmap.md).
