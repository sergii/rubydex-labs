# Decision, verification, and action model

This document defines the boundary between evidence-backed reasoning and operational execution.

## Core idea

A system may identify a Finding, assess a Risk, recommend verification, and propose an Action without being authorized to execute that Action.

```text
Finding / Risk
      ↓
Decision
      ↓
Verification
      ↓
Authorization
      ↓
Action
      ↓
Observation
      ↓
Outcome evaluation
```

The critical invariant is:

> Reasoning authority is not execution authority.

## Why separate these concepts

Without an explicit boundary, an engineering agent can silently move from:

```text
"rollback is probably the safest option"
```

to:

```text
"rollback executed"
```

Those are different operations with different trust, audit, and safety requirements.

## Decision

A Decision records what course of action is selected for a Finding, Risk, Incident, or Change.

Examples:

- verify before acting;
- accept the risk;
- suppress the Finding;
- rollback;
- revert a change;
- add monitoring;
- escalate to an owner;
- take no action yet.

A Decision should retain:

```text
subject refs
candidate options
chosen option
rationale
evidence available at decision time
confidence/belief state
decider identity
recorded_at
```

Decisions are durable history. Later evidence may prove a decision good or bad, but must not rewrite what was known when the decision was made.

## Verification

Verification is an evidence-acquisition operation intended to reduce uncertainty or test a hypothesis before or after an Action.

Examples:

```text
check whether duplicate captures exist
compare error rate before/after deploy
inspect OTEL traces
run a targeted test
query semantic descendants
confirm ownership
verify that rollback restored success rate
```

Verification is not merely prose. It should be represented as a structured request with:

```text
hypothesis / question
required evidence class
scope
success criteria
failure criteria
result evidence refs
status
```

Possible states:

```text
PLANNED
RUNNING
PASSED
FAILED
INCONCLUSIVE
CANCELLED
```

Verification may occur before an Action, after an Action, or both.

## Authorization

Authorization answers a separate question:

> Is this system allowed to execute this Action in this scope now?

Authorization may depend on:

- action class;
- environment;
- blast radius;
- severity;
- reversibility;
- confidence;
- actor identity;
- organization policy;
- explicit human approval;
- emergency policy.

This must not be inferred from model confidence alone.

Example:

```text
Action: restart one stateless dev container
Authorization: policy may allow automatic execution

Action: rollback production payments deployment
Authorization: explicit human approval required
```

## Action

An Action is a concrete state-changing operation.

Examples:

```text
ROLLBACK_DEPLOYMENT
REVERT_CHANGE
RESTART_SERVICE
SCALE_SERVICE
DISABLE_FEATURE_FLAG
ENABLE_FEATURE_FLAG
CREATE_TICKET
PAGE_OWNER
UPDATE_ARCHITECTURE
ADD_MONITORING
SUPPRESS_FINDING
ACKNOWLEDGE_FINDING
```

An Action record should capture:

```text
kind
target refs
parameters
requested_by
authorized_by
authorization policy ref
related decision
related findings/risks/incidents
preconditions
execution state
started_at
completed_at
result evidence refs
rollback action ref
```

## Action lifecycle

```text
PROPOSED
PENDING_VERIFICATION
PENDING_APPROVAL
AUTHORIZED
EXECUTING
SUCCEEDED
FAILED
ROLLED_BACK
CANCELLED
EXPIRED
```

The transition from `PROPOSED` to `AUTHORIZED` is intentionally explicit.

## Preconditions

An authorized Action may still be blocked when preconditions no longer hold.

Example:

```text
Decision at 12:01:
rollback deployment D

At 12:04:
new deployment E already replaced D
```

The executor must re-check relevant preconditions before mutating the system.

Typical preconditions:

```text
target still exists
target revision/deployment is unchanged
finding remains active
risk remains material
approval has not expired
blast radius is within approved bounds
required verification passed
```

This prevents stale reasoning from becoming unsafe execution.

## Reversibility and action risk

Actions themselves introduce Risk.

A useful model distinguishes:

```text
REVERSIBLE
PARTIALLY_REVERSIBLE
IRREVERSIBLE
```

and records expected action blast radius.

A rollback may be reversible operationally while a destructive database migration may not be.

Therefore:

```text
risk of current state
vs
risk of proposed remediation
```

must both be considered by the Decision.

## Decision options are first-class

A Decision should retain rejected alternatives when meaningful.

Example:

```text
Option A: rollback
  benefit: fastest mitigation
  downside: removes unrelated fixes

Option B: feature flag off
  benefit: narrow blast radius
  downside: flag coverage uncertain

Chosen: B
```

This improves later learning and post-incident analysis.

## Outcome evaluation

Action success is not the same as command success.

```text
kubectl rollout undo returned 0
```

only proves that the command completed.

The engineering question is:

```text
Did the undesirable condition improve?
```

Therefore an Action should be followed by Verification and an Outcome Evaluation.

Possible outcome states:

```text
EFFECTIVE
PARTIALLY_EFFECTIVE
INEFFECTIVE
HARMFUL
INCONCLUSIVE
```

Example:

```text
Action: rollback PR-918 deployment
Execution: SUCCEEDED
Verification: duplicate capture rate returned to zero
Outcome: EFFECTIVE
```

or:

```text
Action: restart worker
Execution: SUCCEEDED
Verification: queue latency unchanged
Outcome: INEFFECTIVE
```

## Human approval

Human approval should itself be recorded, not inferred from the fact that an action happened.

Conceptually:

```text
Approval
  actor
  scope
  action_ref
  decision_ref
  granted_at
  expires_at
  constraints
```

Examples of constraints:

```text
only one service
only production-eu-west
only deployment abc123
valid for 10 minutes
maximum 10% traffic
```

## Automation levels

A useful product projection is an explicit autonomy ladder:

```text
L0 OBSERVE
   collect evidence only

L1 RECOMMEND
   Findings, Risks, suggested verification/actions

L2 VERIFY
   automatically collect additional read-only evidence

L3 PREPARE
   construct action plan / command / PR, but do not execute

L4 GUARDED_EXECUTE
   execute only policy-approved bounded actions

L5 CLOSED_LOOP
   execute, verify outcome, rollback/escalate within policy
```

Autonomy is policy and capability, not a personality setting for the model.

Different action kinds and environments may operate at different levels.

## Relationship to Evidence Planner

Verification naturally reuses the evidence acquisition layer:

```text
Decision needs more confidence
        ↓
Verification request
        ↓
EvidencePlan
        ↓
Sensors
        ↓
Evidence
        ↓
Assertions / Confidence
        ↓
Decision update
```

The same planner used to answer questions can therefore support operational verification.

## Relationship to Findings and Risks

A Finding may propose multiple verifications and actions, but it does not execute them.

A Risk may remain `ACCEPTED` with no remediation Action.

An Incident may coordinate several Decisions and Actions.

This keeps the layers separate:

```text
Finding = what deserves attention
Risk = what may happen
Decision = what we choose
Verification = what we check
Authorization = what may execute
Action = what changes state
Outcome = whether it helped
```

## Closed-loop engineering

The resulting operational loop is:

```text
Evidence
  ↓
World Model
  ↓
Finding / Risk
  ↓
Decision
  ↓
Verification
  ↓
Authorization
  ↓
Action
  ↓
Observed Reality
  ↓
Outcome Evaluation
  ↓
World Model / Calibration
```

This is the boundary where an evidence-backed engineering intelligence system can become an agent without losing auditability or control.

## Working invariants

> Reasoning authority is not execution authority.

> Every state-changing Action requires an explicit authorization basis.

> Re-check preconditions at execution time.

> Command success is not outcome success.

> Every meaningful Action should face post-action verification.
