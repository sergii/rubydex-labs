# Incident Model

## Status

Conceptual contract. No benchmark or real OpenAI API execution is required by this document.

## Thesis

An incident is not an alert and not a single finding.

An incident is a durable operational case that groups evolving evidence, findings, risks, hypotheses, decisions, verifications, actions, and observed impact into one time-bounded investigation and response story.

```text
signals
  -> evidence
  -> findings / risks
  -> incident
       -> hypotheses
       -> decisions
       -> verifications
       -> actions
       -> observations
       -> recovery
       -> learning
```

The incident is primarily a coordination and narrative boundary over world-model objects. It must not become a second source of truth that copies facts out of those objects.

## Core invariant

> The incident owns the case. Evidence owns observations. Assertions own claims. Findings own normalized problems. Risks own possible harm. Decisions own choices. Actions own mutations.

The incident links them and preserves their temporal order.

## Incident is not

- an alert notification;
- a raw monitoring event;
- a single finding;
- a mutable prose document containing copied facts;
- a root-cause claim;
- proof that all linked findings share one cause.

Multiple alerts can refer to one finding. Multiple findings can belong to one incident. A finding may exist without an incident. One incident may contain several competing hypotheses.

## Lifecycle

Recommended incident states:

```text
DETECTED
TRIAGED
INVESTIGATING
MITIGATING
MONITORING_RECOVERY
RESOLVED
POSTMORTEM
CLOSED
```

Exceptional states:

```text
MERGED
DUPLICATE
FALSE_ALARM
```

State transitions should be recorded as events rather than inferred only from the current row.

## Severity and confidence

Incident severity describes the operational importance of the incident.

It is distinct from:

- finding severity;
- risk severity;
- confidence in the leading hypothesis;
- confidence that the incident has been fully understood.

An incident may be SEV1 while root-cause confidence is TENTATIVE.

This is normal during response.

## Impact

Incident impact should distinguish at least:

```text
potential impact
realized impact
current impact
peak impact
```

Potential impact comes from risks and predicted consequences.

Realized impact requires observed evidence.

Current and peak impact are temporal projections over observations, not manually rewritten prose when machine evidence exists.

## Blast radius

The incident should link to structured blast-radius evidence where available:

- affected users/accounts;
- requests/jobs;
- percentage of traffic;
- capabilities;
- services/components;
- environments;
- regions;
- data sets;
- financial exposure.

Blast radius is expected to evolve during investigation.

The timeline should therefore preserve statements such as:

```text
10:04  impact unknown
10:09  one region suspected
10:17  4.2% checkout requests affected
10:31  312 accounts confirmed affected
```

Do not overwrite the history with the final number.

## Hypotheses

A hypothesis is an explicit candidate explanation, not a hidden chain-of-thought artifact.

Example:

```text
H1: PR-918 introduced non-idempotent payment retries.
H2: the payment provider emitted duplicate callbacks.
H3: a worker retry policy changed independently of PR-918.
```

Each hypothesis should have:

- stable ID;
- concise claim;
- status;
- confidence record;
- supporting assertion/evidence refs;
- contradicting assertion/evidence refs;
- verification refs;
- created/updated timestamps.

Suggested statuses:

```text
PROPOSED
INVESTIGATING
SUPPORTED
WEAKENED
REFUTED
CONFIRMED
SUPERSEDED
```

A leading hypothesis must never silently delete competing hypotheses.

## Root cause

`root cause` is a conclusion reached after evidence, not a required field at incident creation.

Prefer a structured root-cause assertion/reference when established.

During the incident:

```text
root_cause_state = UNKNOWN | SUSPECTED | SUPPORTED | ESTABLISHED | DISPUTED
```

This prevents premature certainty.

## Timeline

The incident timeline is a projection over immutable or append-only incident events.

Useful event kinds include:

```text
DETECTION
ALERT
FINDING_LINKED
RISK_LINKED
IMPACT_UPDATE
HYPOTHESIS_CREATED
HYPOTHESIS_UPDATED
DECISION
VERIFICATION
ACTION_STARTED
ACTION_COMPLETED
MITIGATION
RECOVERY_SIGNAL
STATUS_CHANGE
HUMAN_NOTE
EXTERNAL_COMMUNICATION
ROOT_CAUSE_UPDATE
```

Each event should distinguish:

- `occurred_at`: when the underlying event happened;
- `recorded_at`: when the system learned or recorded it.

This matters when logs or customer reports arrive late.

## Correlation is not causation

Grouping objects into one incident does not assert causality.

```text
PR deployed at 10:00
latency rose at 10:03
```

is temporal correlation.

A causal assertion requires evidence and should carry its own confidence.

Likewise, two findings occurring together may be:

- same cause;
- cause and consequence;
- independent effects;
- unrelated coincidence.

Incident membership must not encode which one is true.

## Decisions and actions

Incidents reference Decision, Verification, and Action objects rather than duplicating them.

This gives an audit trail:

```text
what was known
  -> what options existed
  -> what was chosen
  -> what verification was required
  -> what was authorized
  -> what was executed
  -> what happened afterward
```

An action succeeding operationally does not prove the incident is resolved.

Recovery requires post-action observation.

## Mitigation versus resolution

Mitigation means harmful behavior has been reduced or stopped sufficiently for the immediate response.

Resolution means the incident's active operational impact is no longer present under the defined recovery criteria.

Root cause may still be unknown after mitigation or even after resolution.

```text
mitigated != understood
resolved != permanently fixed
closed != impossible to recur
```

## Recovery criteria

An incident should define evidence-backed recovery criteria where possible.

Example:

```text
- duplicate payment rate == 0 for 30 minutes
- checkout success rate back within baseline band
- queue backlog below threshold
- no newly affected accounts observed
```

Recovery should be verified, not declared solely because a remediation command returned success.

## Incident fingerprinting and grouping

Do not group incidents only by alert title.

Candidate grouping dimensions:

- affected durable entities;
- finding fingerprints;
- environment/region;
- temporal overlap;
- shared change/deployment refs;
- shared dependency/capability;
- correlated runtime evidence;
- known historical incident pattern.

Grouping can itself have uncertainty.

When uncertain, preserve separate incidents or an explicit probable relationship rather than destructive merging.

## Merge and split

Incident identity must support later correction.

Two incidents may later be found to be one operational event. One incident may later be found to contain two unrelated failures.

Represent merge/split lineage explicitly rather than rewriting history.

## Human communication

Status pages, Slack messages, Telegram alerts, executive summaries, and postmortems are projections of the incident model.

They should not become independent truth stores.

The same incident can render differently for:

```text
on-call engineer -> evidence, hypotheses, actions
engineering lead -> blast radius, owners, decisions
support          -> customer-visible impact
executive        -> severity, impact, recovery status
postmortem       -> timeline, causal analysis, learning
```

## Engineering memory

Closed incidents become high-value evidence for future reasoning.

The system can eventually answer:

```text
Have we seen this pattern before?
Which hypothesis usually explains it?
Which verification discriminates fastest?
Which mitigation worked?
How long did recovery take?
Did the same risk materialize again?
```

Historical incidents should inform future likelihood and decision calibration, but never be treated as proof that the current incident has the same cause.

## Product projections

### Operational

Incident commander view, live impact, timeline, hypotheses, decisions, actions, recovery.

### Overviewable

Highlight affected capabilities/services/components and architecture drift around the incident.

### PR X-Ray

Show whether the current change resembles changes linked to historical incidents and which risks previously materialized.

### Agent interface

Expose machine-readable case state and the next evidence gap without forcing the model to reconstruct the incident from chat history.

## Working invariant

> An incident is a temporal case over evidence-backed objects, not a bag of alerts and not a prose story.

And:

> Preserve uncertainty during response; preserve history after response.
