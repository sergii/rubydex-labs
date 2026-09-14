# Lab 12 status

**DESIGNED — OFFLINE HARNESS FROZEN — MODEL BENCHMARK NOT RUN**

The offline protocol, canonical fixture corpus, deterministic invariants, rendering boundary, exact scorer, deliberate-corruption self-test, and zero-network entrypoint are defined.

Canonical offline command:

```bash
unset OPENAI_API_KEY
bin/lab12-self-test
```

The entrypoint refuses to run when `OPENAI_API_KEY` is present and performs no network or model calls. It runs:

1. fixture validation;
2. deterministic render + exact-score for every fixture;
3. deliberate corruption/mutation self-tests.

The deliberate corruption coverage includes:

- deleted membership item;
- added unexpected item;
- wrong authoritative count;
- duplicate stable key;
- missing provenance backend;
- invalid completeness type;
- incomplete-set wording;
- preservation of distinct stable keys with identical display values.

A prior manual offline dry-run of the self-test logic passed 11/11 checks on representative fixtures. The canonical wrapper is now the frozen execution path for future checkout-local verification.

This is a deterministic harness result only. Conditions A/B/C have not been run against a model, and no result should be reported for those conditions until explicitly authorized and executed.

No real OpenAI API execution is authorized by this status file.

Real API execution requires both repository-level spend authorization and explicit user authorization for a new run. Until then, only offline validation and repository changes are permitted.

Frozen boundary:

```text
backend result
→ EvidenceSet
→ deterministic validation
→ deterministic authoritative rendering
→ optional model explanation
```

Primary success criterion: authoritative membership, count, scope, completeness state, and provenance survive projection without model reconstruction.

The deterministic Lab 12 contract should now remain unchanged unless an offline self-test exposes a preservation bug or a later lab demonstrates that the contract is insufficient.

See [`README.md`](README.md), [`scripts/self-test.py`](scripts/self-test.py), [`../../bin/lab12-self-test`](../../bin/lab12-self-test), and [`../../docs/api-spend-safety.md`](../../docs/api-spend-safety.md).
