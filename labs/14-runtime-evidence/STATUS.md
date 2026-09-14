# Lab 14 status

**DESIGNED — OFFLINE RUNTIME-EVIDENCE HARNESS ADDED — NOT RUN AGAINST REAL TELEMETRY**

Lab 14 now defines runtime evidence semantics around bounded `OBSERVED` assertions rather than generic telemetry ingestion.

Current deterministic boundary:

```text
runtime sensor output
→ coverage / sampling evaluation
→ identity check
→ OBSERVED Assertion or fail-closed refusal
→ Lab 13 comparison / finding pipeline
```

Frozen coverage states:

- `COMPLETE_FOR_SCOPE`
- `PARTIAL`
- `SAMPLED`
- `UNKNOWN`

Frozen guardrails:

> Runtime evidence establishes what was observed within a bounded scope and time window. It does not establish what always happens.

> No observation is not evidence of no behavior unless the observation contract establishes completeness for that exact scope and window.

The offline fixture corpus currently covers sampled call presence, sampled call absence, exhaustive zero events in a complete scope, missing observation window, bounded metric values, and unresolved runtime identity.

The self-test verifies:

- runtime-derived claims are `OBSERVED`;
- observation windows become `valid_time`;
- environment and filters survive normalization;
- evidence references survive normalization;
- sampling/coverage metadata is preserved;
- sampled/partial absence claims fail closed;
- large sample counts and high sampling rates do not magically create completeness;
- unresolved runtime names require identity resolution;
- source runtime observations remain unchanged.

Canonical offline command:

```bash
make lab14-self-test
```

The wrapper removes `OPENAI_API_KEY`, performs no network/model/telemetry-backend calls, and executes only local fixture normalization tests.

The harness has been added to the repository, but this status does not claim a canonical checkout-local PASS yet. Real OpenTelemetry/log/metrics integration has not been run.

No real OpenAI API execution is authorized by this status file. No model benchmark has been run.

No new durable `RuntimeObservation` object has been introduced. Lab 14 intentionally tests whether existing Evidence + Assertion primitives are sufficient before adding another abstraction.

See [`README.md`](README.md) and [`../../docs/runtime-evidence-model.md`](../../docs/runtime-evidence-model.md).
