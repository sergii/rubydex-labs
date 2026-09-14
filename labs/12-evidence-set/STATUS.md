# Lab 12 status

**DESIGNED — OFFLINE SELF-TEST ADDED — MODEL BENCHMARK NOT RUN**

The offline protocol, fixture classes, deterministic invariants, rendering boundary, scoring rules, and corruption self-test are defined.

The self-test covers baseline validity plus deliberate corruption cases including:

- deleted membership item;
- added unexpected item;
- wrong authoritative count;
- duplicate stable key;
- missing provenance backend;
- invalid completeness type;
- incomplete-set wording;
- preservation of distinct stable keys with identical display values.

A manual offline dry-run of the self-test logic passed 11/11 checks on representative fixtures. This is a deterministic harness check, not a model benchmark and not evidence for Lab 12 conditions A/B/C yet.

No real OpenAI API execution is authorized by this status file.

Real API execution requires both repository-level spend authorization and explicit user authorization for a new run. Until then, only offline validation and repository changes are permitted.

Current objective:

```text
backend result
→ EvidenceSet
→ deterministic validation
→ deterministic authoritative rendering
→ optional model explanation
```

Primary success criterion: authoritative membership, count, scope, completeness state, and provenance survive projection without model reconstruction.

Next offline step: execute the self-test against the canonical repository fixture corpus from a checkout or CI path that performs zero external/model calls, then freeze those deterministic results before any future A/B/C model comparison.

See [`README.md`](README.md), [`scripts/self-test.py`](scripts/self-test.py), and [`../../docs/api-spend-safety.md`](../../docs/api-spend-safety.md).
