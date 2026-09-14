# Lab 13 status

**DESIGNED — COMPARISON BOUNDARY FROZEN OFFLINE — MODEL BENCHMARK NOT RUN**

The evidence-fusion protocol is defined around machine-owned assertion comparison rather than free-form model fusion.

Current deterministic boundary:

```text
assertions
→ identity alignment
→ predicate semantic alignment
→ scope / revision / environment / valid-time alignment
→ ComparisonRecord
→ optional ConflictRecord
→ optional derived assertion / Finding
```

Frozen comparison outcomes currently include:

- `COMPATIBLE`;
- `NON_COMPARABLE_PREDICATE`;
- `IDENTITY_UNRESOLVED`;
- `SCOPE_MISMATCH`;
- `TEMPORAL_MISMATCH`;
- `REVISION_MISMATCH`;
- `ENVIRONMENT_MISMATCH`;
- `DECLARED_VS_OBSERVED_DRIFT`;
- `CONTRADICTION`;
- `INSUFFICIENT_EVIDENCE`.

`ComparisonRecord` is now first-class in `schemas/comparison.schema.json`. It separates `comparison_class` from `conflict_state` (`NONE`, `EXPLAINED`, `ACTIVE`, `RESOLVED`). Benign mismatches and unresolved comparability remain comparisons only; they do not create conflicts.

A `ConflictRecord` is appropriate only for the subset of comparisons that establish an active conflict, such as sufficiently aligned `CONTRADICTION` or authoritative declared-vs-observed drift.

The initial offline fixture corpus covers compatible semantic/runtime evidence, declared-vs-observed drift, same-name/different-identity, revision mismatch, environment mismatch, deterministic contradiction, non-overlapping runtime windows, and independent corroboration.

False-conflict mutation tests enforce that changing environment, revision, non-overlapping valid time, entity identity, or predicate comparability cannot accidentally upgrade a benign mismatch into `CONTRADICTION`.

The ComparisonRecord self-test additionally enforces:

- benign comparison classes have `conflict_state = NONE` and no `conflict_ref`;
- active contradiction/drift classes have `conflict_state = ACTIVE` and an explicit conflict reference;
- source assertion references and alignment dimensions remain present.

Canonical offline command:

```bash
make lab13-self-test
```

The wrapper removes `OPENAI_API_KEY` from its environment and performs no network or model calls. It runs:

1. frozen comparison fixtures;
2. false-conflict mutation tests;
3. ComparisonRecord → ConflictRecord boundary tests.

No real OpenAI API execution is authorized by this status file. No model benchmark has been run.

Frozen guardrail:

> Comparison is broader than conflict. Conflict classification is allowed only after identity, predicate semantics, scope, revision, environment, and time are sufficiently aligned.

The conceptual cleanup from the earlier `ConflictRecord` design is now validated enough to use going forward without destructively migrating the v1 conflict schema during Lab 13.

See [`README.md`](README.md), [`../../docs/comparison-model.md`](../../docs/comparison-model.md), and [`../../schemas/comparison.schema.json`](../../schemas/comparison.schema.json).
