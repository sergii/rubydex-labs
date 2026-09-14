# Lab 13 status

**DESIGNED — OFFLINE COMPARATOR ADDED — MODEL BENCHMARK NOT RUN**

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

Canonical offline command:

```bash
make lab13-self-test
```

The wrapper unsets/refuses `OPENAI_API_KEY` and performs no network or model calls. It runs the deterministic comparator against the frozen fixture corpus and expects exact classifications.

No real OpenAI API execution is authorized by this status file. No model benchmark has been run.

Next offline step: execute and freeze the comparator result, then add deliberate mutation tests for false-conflict prevention before considering any model-assisted M1/M2/M3 comparison.
