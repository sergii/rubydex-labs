# Lab 13 status

**DESIGNED — COMPARISON + IDENTITY + FINDING PROJECTION BOUNDARIES FROZEN OFFLINE — MODEL BENCHMARK NOT RUN**

The evidence-fusion protocol is defined around machine-owned assertion comparison rather than free-form model fusion.

Current deterministic boundary:

```text
assertions
→ identity alignment
→ predicate semantic alignment
→ scope / revision / environment / valid-time alignment
→ ComparisonRecord
→ optional ConflictRecord
→ optional Finding candidate
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

`ComparisonRecord` is first-class in `schemas/comparison.schema.json`. It separates `comparison_class` from `conflict_state` (`NONE`, `EXPLAINED`, `ACTIVE`, `RESOLVED`). Benign mismatches and unresolved comparability remain comparisons only; they do not create conflicts.

A `ConflictRecord` is appropriate only for the subset of comparisons that establish an active conflict, such as sufficiently aligned `CONTRADICTION` or authoritative declared-vs-observed drift.

Lab 13 also validates a narrower identity boundary:

```text
Identity / representation relations:
SAME_AS
RENAMED_FROM
MOVED_FROM
REPRESENTS
OBSERVED_AS

provisional representation relation:
DEPLOYED_AS

ordinary domain assertions:
IMPLEMENTED_BY
OWNED_BY
SERVES_CAPABILITY
DERIVED_FROM
```

The legacy `identity-link.schema.json` remains unchanged during Lab 13. New code should treat domain relations as evidence-backed assertions rather than identity links. `DEPLOYED_AS` remains under review because it may represent either representation mapping or an ordinary operational relation depending on semantics.

The finding-projection boundary is also frozen offline. `finding.schema.json` now has optional `comparison_refs` so lineage from a human-facing Finding back to its ComparisonRecord is explicit rather than hidden in metadata.

Initial deterministic projection rules are deliberately narrow:

```text
DECLARED_VS_OBSERVED_DRIFT + ACTIVE
→ ARCHITECTURE_DRIFT

CONTRADICTION + ACTIVE
→ EVIDENCE_CONFLICT
```

Benign or unresolved comparison classes do not create a Finding candidate merely because two records differ.

A projected Finding must preserve:

- all source assertion refs;
- the originating comparison ref;
- the conflict ref when present;
- the union of relevant source evidence refs;
- stable subject entity refs.

Creating a Finding never mutates the source Assertions. Finding severity remains independent of confidence, and a Finding is not action authorization.

Canonical offline command:

```bash
make lab13-self-test
```

The wrapper removes `OPENAI_API_KEY` from its environment and performs no network or model calls. It runs:

1. frozen comparison fixtures;
2. false-conflict mutation tests;
3. ComparisonRecord → ConflictRecord boundary tests;
4. IdentityLink → Assertion boundary tests;
5. Comparison/Conflict → Finding lineage tests.

No real OpenAI API execution is authorized by this status file. No model benchmark has been run.

Frozen guardrails:

> Comparison is broader than conflict. Conflict classification is allowed only after identity, predicate semantics, scope, revision, environment, and time are sufficiently aligned.

> If a relationship can change while both endpoint entities remain the same durable entities, model it as an Assertion by default rather than an IdentityLink.

> A Finding is a projection of an evidence-backed problem, not a replacement for the Assertions, Comparison, Conflict, or Evidence that justify it.

The conceptual cleanup from the earlier broad `ConflictRecord` and `IdentityLink` designs is now validated enough to use going forward without destructively migrating the v1 schemas during Lab 13.

See [`README.md`](README.md), [`../../docs/comparison-model.md`](../../docs/comparison-model.md), [`../../docs/identity-boundary.md`](../../docs/identity-boundary.md), [`../../docs/finding-projection.md`](../../docs/finding-projection.md), and [`../../schemas/comparison.schema.json`](../../schemas/comparison.schema.json).
