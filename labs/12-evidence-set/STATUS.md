# Lab 12 status

**DESIGNED — NOT RUN**

The offline protocol, fixture classes, deterministic invariants, rendering boundary, and scoring rules are defined.

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

See [`README.md`](README.md) and [`../../docs/api-spend-safety.md`](../../docs/api-spend-safety.md).
