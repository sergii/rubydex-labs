# Confidence and belief model

This document defines a research model for confidence in the evidence-backed software world model.

## Core rule

Confidence is not a decorative probability emitted by an LLM.

A useful confidence value must be derived from explicit evidence properties and reconciliation state.

```text
confidence
  !=
"the model feels 83% sure"
```

Instead:

```text
confidence
  <- source strength
  <- completeness
  <- freshness
  <- scope match
  <- corroboration
  <- contradiction
  <- identity resolution quality
  <- derivation depth
  <- historical calibration
```

## What confidence applies to

Confidence belongs to a claim or resolution, not to the entire system globally.

Examples:

- confidence that a semantic relationship set is complete for revision `abc123`;
- confidence that an OTEL resource maps to a durable service identity;
- confidence that an architecture policy still applies;
- confidence that a derived consequence follows from its supporting assertions;
- confidence that a pre-deploy prediction will occur.

These are different confidence questions and should not share one arbitrary score without an explanation of how it was produced.

## Confidence dimensions

A scalar may be useful for ranking, but the system should preserve the underlying dimensions.

### Source strength

How strongly can the source establish this kind of claim?

Examples:

```text
Rubydex resolved reference at pinned revision
  -> strong for semantic membership
  -> says nothing about runtime execution

OTEL trace
  -> strong for observed execution in the sampled window
  -> does not prove impossible paths never occur

Architecture declaration
  -> strong for intended policy
  -> not proof of actual runtime compliance
```

### Completeness

Can the source establish a complete set for the declared scope?

```text
COMPLETE
PARTIAL
UNKNOWN
NOT_APPLICABLE
```

Completeness is especially important for `all`, `every`, `complete`, blast-radius, and coverage questions.

### Freshness

How current is the evidence for the question being answered?

Freshness is not a single universal timeout. It depends on evidence class.

Examples:

- a semantic result pinned to the exact Git revision is fresh for that revision indefinitely;
- production latency evidence may become stale within minutes or hours;
- ownership metadata may remain valid for weeks but still require an effective-time boundary;
- architecture policy may be revisioned rather than wall-clock fresh.

### Scope match

Evidence must match the scope of the assertion.

Dimensions may include:

```text
repository / revision
environment
service
region
time window
production vs test
core vs plugins
request cohort
```

Evidence from the wrong scope should reduce or invalidate confidence rather than being silently generalized.

### Corroboration

Independent sensors can support the same claim.

Example:

```text
semantic: checkout may call payments
runtime: checkout was observed calling payments
architecture: checkout is allowed to call payments
```

These observations increase confidence in different aspects of the relationship, but they must not be double-counted as independent if they derive from the same underlying source.

### Contradiction

Conflicting evidence lowers confidence or changes the claim status.

Example:

```text
DECLARED owner = payments-team
OBSERVED deployment metadata owner = commerce-platform
```

The correct result may be `CONFLICTED`, not a lower-but-still-active blended score.

### Identity resolution quality

Cross-sensor evidence can be fused only if the underlying entities are resolved with sufficient confidence.

If:

```text
payments-api ~= OTEL service "payments"
```

is only `PROBABLE`, any assertion produced by joining their evidence must inherit that uncertainty.

### Derivation depth

A deterministic first-order fact and a long inference chain should not have identical epistemic status.

```text
Rubydex result
  -> deterministic assertion

semantic + policy
  -> derived consequence

semantic + policy + historical runtime pattern
  -> prediction
```

Derived and predicted claims should expose the chain they depend on.

### Historical calibration

Predicted assertions eventually have outcomes.

If a predictor historically emits `0.8` confidence but only 45% of such predictions are confirmed, its raw confidence is poorly calibrated.

Lab 16 should eventually make empirical calibration possible.

## Belief state before score

The system should determine an epistemic state before calculating any scalar confidence.

Suggested states:

```text
ESTABLISHED
SUPPORTED
TENTATIVE
UNKNOWN
CONFLICTED
REFUTED
STALE
```

Examples:

```text
ESTABLISHED
  deterministic evidence fully establishes the scoped fact

SUPPORTED
  multiple appropriate evidence sources support it

TENTATIVE
  plausible but depends on incomplete or unresolved evidence

UNKNOWN
  insufficient evidence

CONFLICTED
  credible evidence sources disagree

REFUTED
  stronger evidence contradicts the claim

STALE
  evidence was once relevant but does not satisfy current freshness requirements
```

A numeric score must not hide these categorical differences.

For example, `CONFLICTED 0.55` and `TENTATIVE 0.55` mean very different things.

## Do not average heterogeneous truth sources

A naive formula such as:

```text
(Rubydex + OTEL + architecture) / 3
```

is invalid.

Each source establishes different predicates and scopes. The confidence engine must reason about compatibility first.

For example:

```text
semantic possible dependency
runtime observed dependency
architecture allowed dependency
```

are not three votes on one boolean proposition. They are three related assertions that can jointly support a higher-level conclusion.

## Deterministic confidence boundaries

Some facts should not use fuzzy confidence at all.

For a pinned revision and complete deterministic query:

```text
membership in EvidenceSet
count
query scope
provenance
```

should be treated as established machine facts, not assigned `0.97` by an LLM.

Uncertainty may still exist in:

- whether the query scope is the correct one for the user question;
- whether the semantic relation implies business impact;
- whether the relationship is exercised at runtime;
- whether identity mapping to another sensor is correct.

The location of uncertainty matters.

## Confidence propagation

Derived assertions must not become stronger than unsupported dependencies.

A useful conservative rule is:

```text
derived confidence <= weakest required dependency confidence
```

but production logic may need a richer model for independent corroboration.

Example:

```text
identity mapping confidence = 0.72
runtime observation confidence = established

cross-sensor derived claim
  cannot have confidence > identity mapping confidence
```

Likewise, a consequence depending on an unresolved architecture mapping cannot become `ESTABLISHED` simply because the semantic evidence is deterministic.

## Proposed confidence record

Confidence should be inspectable.

```json
{
  "state": "SUPPORTED",
  "score": 0.86,
  "dimensions": {
    "source_strength": 1.0,
    "completeness": 1.0,
    "freshness": 0.95,
    "scope_match": 1.0,
    "identity_resolution": 0.82,
    "corroboration": 0.9,
    "contradiction": 1.0
  },
  "method": "rules-v1",
  "explanation": [
    "semantic set is complete for pinned revision",
    "runtime observation matches the same service with probable identity resolution",
    "no active conflicting assertion"
  ]
}
```

The scalar is secondary. The dimensions, state, method, and explanation are the auditable artifact.

## Rules before ML

The first implementation should be deterministic and conservative.

Start with explicit rules such as:

```text
if credible conflict exists:
    state = CONFLICTED

elif required evidence is missing:
    state = UNKNOWN

elif evidence is outside freshness policy:
    state = STALE

elif deterministic complete evidence directly establishes claim:
    state = ESTABLISHED

elif all required evidence is present with resolved identities:
    state = SUPPORTED

else:
    state = TENTATIVE
```

Only after outcomes accumulate should learned calibration be considered.

## Evidence planner interaction

Confidence should influence evidence acquisition.

```text
request
  -> initial EvidencePlan
  -> gather evidence
  -> evaluate belief state
  -> if insufficient:
         acquire additional evidence
  -> otherwise reason / answer
```

This introduces an important concept:

> Evidence planning can be iterative rather than one-shot.

A cheap first plan may be sufficient. If identity is ambiguous, evidence stale, or claims conflict, the planner can escalate selectively.

## Product behavior

The UI should not primarily show arbitrary percentages.

Prefer human-meaningful states:

```text
Established
Supported
Tentative
Conflicted
Unknown
Stale
```

with drill-down into:

- supporting sensors;
- scope;
- freshness;
- conflicts;
- missing evidence;
- identity uncertainty;
- prediction calibration where relevant.

Percentages can be useful for machine ranking and advanced inspection, but should not create false precision.

## Research implications

The confidence layer spans several future labs:

```text
Lab 12
  completeness and machine-owned evidence

Lab 13
  corroboration and conflict across evidence classes

Lab 14
  freshness and observed runtime truth

Lab 15
  temporal validity and stale evidence

Lab 16
  prediction calibration against observed outcomes
```

A dedicated confidence benchmark may eventually be justified, but the model should first be exercised inside these existing research stages.

## Working invariant

> Confidence is an auditable property of evidence-backed claims, not a personality trait of the model.
