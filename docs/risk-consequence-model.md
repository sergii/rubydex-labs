# Risk and consequence model

This document defines the semantic boundary between an observed engineering problem, a current risk, a predicted consequence, and realized impact.

The goal is to let pre-deploy analysis, runtime operations, and incident review speak the same language without pretending that a possible future outcome is the same thing as an observed failure.

## Core distinction

```text
OBSERVED PROBLEM
    something undesirable is already evidenced now

CURRENT RISK
    a harmful outcome is possible under the current system state

PREDICTED CONSEQUENCE
    a future outcome is forecast for a proposed change or condition

ACTUAL IMPACT
    a harmful outcome has been observed to affect users, systems, money, data, or operations
```

These concepts are related but not interchangeable.

## Example

Before deployment:

```text
Change: PR-918
Risk: duplicate payment capture is possible
Predicted consequence: some checkout attempts may charge twice
```

After deployment, if traces and payment records confirm duplicate capture:

```text
Observed problem: duplicate capture path executed
Actual impact: 14 customers were charged twice
```

The prediction should not be rewritten into the observation. The system should preserve both and connect them through evaluation.

## Why the distinction matters

Without this separation, systems tend to make category errors such as:

- presenting a speculative PR risk as if an incident is already happening;
- presenting a runtime anomaly as if customer impact has been established;
- treating a severe possible consequence as equivalent to high confidence;
- losing the original prediction after reality is observed;
- failing to distinguish exposure from realized damage.

## Risk

A Risk is a structured statement about a plausible harmful outcome that has not necessarily occurred.

Conceptually:

```text
hazard / initiating condition
      |
      v
exposed entity or flow
      |
      v
possible consequence
      |
      v
likelihood / uncertainty
      |
      v
potential impact
```

A risk should reference the evidence and assertions that justify its existence.

Examples:

```text
A non-idempotent webhook handler may create duplicate captures.

A checkout change may increase dependency fan-out and latency.

A missing owner for a critical queue may increase recovery time during incidents.
```

Risk is not itself proof that harm occurred.

## Consequence

A Consequence describes what follows if a condition, change, or risk pathway materializes.

Useful consequence classes include:

```text
USER_EXPERIENCE
RELIABILITY
PERFORMANCE
DATA_INTEGRITY
FINANCIAL
SECURITY
COMPLIANCE
OPERABILITY
DELIVERY
ARCHITECTURE
```

Examples:

```text
orders may remain unconfirmed
customers may be charged twice
p95 latency may exceed the checkout SLO
ledger records may diverge from successful captures
on-call investigation time may increase
```

Consequences may be predicted, derived, or observed.

## Impact

Impact is realized consequence backed by observation.

Impact should answer, where evidence permits:

```text
who or what was affected?
how many?
where?
for how long?
how severely?
what value, money, data, or availability was lost?
```

Typical impact dimensions:

```text
users / accounts
requests / jobs
business capabilities
regions / environments
duration
financial exposure or realized loss
data integrity
SLO / error-budget consumption
operational effort
```

A runtime symptom without evidence of affected users or business behavior may still be an observed problem while impact remains unknown.

## Potential versus realized impact

The model must distinguish:

```text
potential_impact
    what could happen if the risk materializes

realized_impact
    what evidence shows actually happened
```

For example:

```text
Potential:
all checkout customers could be affected

Realized:
14 of 18,200 checkout attempts were affected
```

These numbers should never be silently substituted for one another.

## Severity

Severity describes the magnitude of a consequence or impact, not confidence that it exists.

Suggested ordinal scale:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Severity should be driven by impact dimensions such as:

- user/customer harm;
- business criticality;
- data corruption or irreversibility;
- financial loss;
- security/compliance exposure;
- blast radius;
- duration;
- recovery difficulty.

A `CRITICAL` predicted consequence can still have `TENTATIVE` confidence.

## Likelihood

Risk likelihood is distinct from confidence.

```text
confidence
    how strongly evidence supports the risk assertion

likelihood
    how likely the harmful pathway is to occur
```

A system may be highly confident that a rare failure mode exists.

Example:

```text
confidence = ESTABLISHED
likelihood = RARE
severity = CRITICAL
```

This could describe a deterministic race condition requiring an unusual timing window but capable of causing duplicate financial transactions.

Suggested likelihood categories:

```text
UNKNOWN
RARE
UNLIKELY
POSSIBLE
LIKELY
ALMOST_CERTAIN
```

Numeric probability should be optional and only used when justified by calibrated historical or statistical evidence.

## Risk state

Suggested lifecycle:

```text
IDENTIFIED
ASSESSING
ACTIVE
MITIGATED
ACCEPTED
MATERIALIZED
EXPIRED
DISPROVEN
```

`MATERIALIZED` means the risk pathway produced an observed consequence or impact. It does not mean the original risk record should be deleted.

## Prediction evaluation

A predicted consequence should later be evaluated against observed reality.

Possible outcomes:

```text
CONFIRMED
PARTIALLY_CONFIRMED
NOT_OBSERVED
CONTRADICTED
INCONCLUSIVE
NOT_YET_EVALUABLE
```

This is the bridge to Lab 16 and future calibration.

Example:

```text
PREDICTED:
PR-918 may increase checkout p95 above 500 ms

OBSERVED:
p95 increased from 340 ms to 610 ms after deployment

EVALUATION:
CONFIRMED
```

The original prediction remains immutable/history-preserving.

## Relationship to Finding

A Finding is the product-facing normalized engineering problem or risk surfaced to a human.

A Finding may reference:

```text
observed problem
risk
predicted consequence
actual impact
```

Examples:

```text
PR X-Ray Finding
    type: CHANGE_RISK
    risk: duplicate captures are possible
    predicted consequence: customers may be charged twice

Operational Finding
    type: DATA_INTEGRITY_RISK
    observed problem: duplicate capture path observed
    actual impact: 14 customers charged twice
```

The same underlying risk lineage can therefore appear before and after deployment without collapsing prediction into observation.

## Risk lineage

A useful chain is:

```text
Change / Condition
       |
       v
Risk
       |
       v
Predicted Consequence
       |
       v
Verification / Deployment
       |
       v
Observed Problem
       |
       v
Actual Impact
       |
       v
Prediction Evaluation
```

This lineage is one of the key temporal structures of the software world model.

## Human-facing consequence first

The user-facing layer should prefer business and operational consequences over implementation trivia.

Instead of:

```text
Payments::CaptureJob references Payments::Gateway
```

prefer, when supported:

```text
This change reaches the payment-capture path.
If retries become non-idempotent, customers could be charged more than once.
```

Implementation evidence remains available for drill-down and verification.

## Current architectural position

```text
Evidence
  -> Identity
  -> Assertions
  -> Conflict / Confidence
  -> World Model
  -> Risk / Consequence
  -> Finding
  -> Verification / Action
  -> Observation
  -> Impact / Calibration
```

Risk and consequence are therefore not merely UI labels. They are the bridge between machine-established facts and human engineering decisions.

## Working invariants

1. A possible consequence is not an observed impact.
2. Severity is not confidence.
3. Likelihood is not confidence.
4. Potential impact is not realized impact.
5. Predictions remain preserved after observation.
6. Actual impact requires observational evidence.
7. Risk lineage should survive deployment and incident resolution.
8. Human-facing output should emphasize consequences while preserving drill-down to evidence.

> Facts establish the world. Risks describe what may happen. Consequences describe what follows. Impact records what actually happened.
