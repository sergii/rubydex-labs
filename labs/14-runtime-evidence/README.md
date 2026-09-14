# Lab 14 — runtime evidence semantics

> **Status: DESIGNED — OFFLINE HARNESS IN PROGRESS — NOT RUN AGAINST REAL TELEMETRY**

## Research question

Can runtime telemetry be converted into evidence-backed `OBSERVED` assertions without overstating what was actually observed?

The goal is not "ingest OpenTelemetry". The goal is to preserve the epistemic limits of runtime data.

## Core invariant

> Runtime evidence establishes what was observed within a bounded scope and time window. It does not establish what always happens.

Examples:

```text
100 sampled traces contained checkout-service -> payments-api
```

may support:

```text
OBSERVED checkout-service --called--> payments-api
valid_time = sampled window
```

It does **not** support:

```text
checkout-service always calls payments-api
```

Likewise, absence of a call in sampled traces does not establish that the call never happened.

## No new durable object yet

Lab 14 deliberately starts with existing primitives:

```text
runtime sensor output
→ Evidence / EvidenceSet
→ OBSERVED Assertion
→ ComparisonRecord
→ optional Finding
```

Do not introduce a durable `RuntimeObservation` model unless fixtures prove that Evidence + Assertion cannot represent the required semantics without loss.

## Runtime evidence contract

Every runtime observation used to create an assertion must preserve at least:

- source/backend;
- environment;
- observation window (`from`, `to`);
- subject identity or unresolved representation;
- predicate / measured fact;
- object/value;
- sample count where applicable;
- sampling mode / sampling rate when known;
- coverage state;
- filters (region, route, tenant, service, status, etc.);
- evidence provenance;
- whether absence claims are permitted.

## Coverage states

Runtime evidence must distinguish:

```text
COMPLETE_FOR_SCOPE
PARTIAL
SAMPLED
UNKNOWN
```

`COMPLETE_FOR_SCOPE` is rare and must refer to an explicit scope and window.

`SAMPLED` means observed membership can establish presence but normally cannot establish exhaustive absence.

`UNKNOWN` must not be silently interpreted as complete.

## Presence versus absence

Presence is easier to establish than absence.

```text
observed event/call/error
→ may create positive OBSERVED assertion
```

But:

```text
not observed
```

may create a negative/exhaustive assertion only when coverage is sufficient for the stated scope.

Guardrail:

> No observation is not evidence of no behavior unless the observation contract establishes completeness for that exact scope and window.

## Proposed offline scenarios

1. `sampled-call-present` — sampled traces observe A calling B; positive assertion allowed.
2. `sampled-call-absent` — sampled traces do not contain A→B; negative assertion forbidden.
3. `complete-health-check-failure` — every expected check in a bounded window is accounted for; failure assertion allowed.
4. `partial-log-error` — logs show error presence; presence assertion allowed, error-rate completeness unknown.
5. `metric-window-value` — metric aggregate produces bounded scalar assertion with explicit window.
6. `different-environment` — production observation must not be generalized to staging.
7. `different-window` — yesterday's observation must not become current truth.
8. `sampling-rate-known` — assertion carries sampling metadata/provenance.
9. `sampling-rate-unknown` — confidence/coverage must remain limited.
10. `zero-events-complete-scope` — exhaustive zero is allowed only with `COMPLETE_FOR_SCOPE`.
11. `identity-unresolved-runtime-name` — `service.name` alone does not create durable entity identity.
12. `filtered-observation` — region/route filters survive into scope.

## Assertion mapping

Runtime-derived claims use:

```text
kind = OBSERVED
```

and must preserve a bounded `valid_time`.

Examples:

```text
OBSERVED
checkout-service --called--> payments-api
valid_time: 2026-09-14T12:00Z..12:05Z
scope.environment: production
```

```text
OBSERVED
payments-api --error_count--> 17
valid_time: 2026-09-14T12:00Z..12:05Z
```

The original runtime evidence remains immutable and referenced through `evidence_refs`.

## Machine-owned invariants

1. Runtime-derived assertions are `OBSERVED`, never silently `DETERMINISTIC`.
2. Every runtime assertion has an observation window.
3. Environment is preserved when known.
4. Filters are preserved rather than dropped during normalization.
5. Presence may be asserted from partial/sampled data if actually observed.
6. Absence/exhaustiveness requires `COMPLETE_FOR_SCOPE` for the exact scope.
7. Sampling metadata is never converted into implied completeness.
8. Unknown sampling/coverage stays unknown.
9. Runtime names do not establish durable identity by themselves.
10. A later observation does not rewrite an earlier assertion; it creates another time-scoped assertion.
11. Conflicting observations from different windows are temporal differences before they are contradictions.
12. Provenance survives Evidence → Assertion conversion.

## Offline harness

Lab 14 first tests deterministic normalization only:

```text
runtime fixture
→ validate observation contract
→ build OBSERVED assertion or refuse
→ validate preserved scope/window/coverage/provenance
```

No model is needed.

Canonical command once the harness is frozen:

```bash
make lab14-self-test
```

## Fail-closed rules

If observation window is missing:

```text
REFUSE_ASSERTION
```

If a negative claim is requested from sampled/partial/unknown coverage:

```text
REFUSE_ASSERTION
```

If runtime identity is unresolved:

```text
preserve representation + require identity resolution
```

not silent name-based fusion.

If environment/scope is missing, do not invent it.

## Relationship to Lab 13

Lab 13 established that different truth domains remain distinct:

```text
DETERMINISTIC references
DECLARED allowed_dependency
OBSERVED called
```

Lab 14 defines what is required before a runtime sensor is allowed to produce the `OBSERVED` side of that comparison.

## Safety

The offline harness must make zero network, telemetry-backend, model, or OpenAI API calls.

Real telemetry integration and any model benchmark remain unexecuted until explicitly authorized.
