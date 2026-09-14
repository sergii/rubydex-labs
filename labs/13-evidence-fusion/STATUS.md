# Lab 13 status

**DESIGNED — OFFLINE COMPARATOR + FALSE-CONFLICT GUARDRAILS ADDED — MODEL BENCHMARK NOT RUN**

The evidence-fusion protocol is defined around machine-owned assertion comparison rather than free-form model fusion.

Current deterministic boundary:

```text
assertions
→ identity alignment
→ predicate semantic alignment
→ scope / revision / environment / valid-time alignment
→ comparison classification
→ optional conflict / derived assertion / finding candidate
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

The initial offline fixture corpus covers compatible semantic/runtime evidence, declared-vs-observed drift, same-name/different-identity, revision mismatch, environment mismatch, deterministic contradiction, non-overlapping runtime windows, and independent corroboration.

False-conflict mutation tests additionally enforce that changing environment, revision, non-overlapping valid time, entity identity, or predicate comparability cannot accidentally upgrade a benign mismatch into `CONTRADICTION`. True contradictory aligned assertions remain contradictory, and declared-vs-observed policy drift remains a distinct outcome.

Canonical offline command:

```bash
make lab13-self-test
```

The wrapper removes `OPENAI_API_KEY` from its environment and performs no network or model calls. It runs both the frozen fixture comparator and the false-conflict mutation self-test.

No real OpenAI API execution is authorized by this status file. No model benchmark has been run.

Frozen guardrail:

> Conflict classification is allowed only after identity, predicate semantics, scope, revision, environment, and time are sufficiently aligned.

Next offline step: add machine-readable comparison output / comparison-record contract so Lab 13 can feed the world model without turning every comparison into a `ConflictRecord`.
