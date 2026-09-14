# Engineering Memory / Learning Model

## Thesis

The system should not remember everything. It should retain evidence-backed lessons that improve future prediction, triage, verification, routing, and remediation.

> Raw events are history. Engineering memory is validated, scoped, revisable knowledge extracted from that history.

Engineering memory is not a chat transcript, vector store, incident archive, or bag of summaries. Those may be sources. The durable memory unit is a versioned learning record with provenance, scope, applicability, confidence, supporting and contradicting observations, and explicit invalidation rules.

## Why a separate memory layer exists

The world model answers: what do we currently believe about the software system?

Engineering memory answers: what have we learned from repeated changes, predictions, incidents, verifications, actions, and outcomes that should influence future reasoning?

The distinction matters because many useful lessons are not direct facts about the current system. Examples:

- changes to payment retry logic have repeatedly caused duplicate-capture risk;
- runtime traces are the fastest discriminator for this class of incident;
- restarting workers usually clears symptom X but rarely fixes root cause Y;
- architecture declarations for service Z become stale quickly after ownership transfers;
- predictions about queue saturation have historically been overconfident;
- a specific verification step has high information gain for a recurring hypothesis class.

These are learned operational regularities, not source-code facts.

## Pipeline

```text
change / prediction / deploy / incident / verification / action / outcome
                              ↓
                       historical evidence
                              ↓
                      candidate learning
                              ↓
                     validation / scope
                              ↓
                     engineering memory
                              ↓
            future planner / reasoning / triage
                              ↓
                        new observations
                              ↓
                reinforce / weaken / supersede
```

## Memory kinds

Initial taxonomy:

- `RISK_PATTERN` — recurring relation between a condition/change shape and a risk.
- `CONSEQUENCE_PATTERN` — recurring consequence after a class of precursor conditions.
- `DIAGNOSTIC_HEURISTIC` — evidence source or verification that efficiently discriminates hypotheses.
- `REMEDIATION_EFFECTIVENESS` — observed effectiveness of an action under a stated scope.
- `FAILURE_MODE` — recurring operational or correctness failure pattern.
- `SYSTEM_INVARIANT` — repeatedly validated constraint that should remain true.
- `ROUTING_HEURISTIC` — which evidence backends are useful for a task shape.
- `OWNERSHIP_KNOWLEDGE` — learned durable ownership or escalation pattern, subject to freshness.
- `CALIBRATION_RECORD` — historical prediction accuracy for a model/pattern/scope.
- `ANTI_PATTERN` — action or reasoning pattern repeatedly associated with poor outcomes.
- `PLAYBOOK_STEP` — validated step that is useful in a recurring investigation or response.
- `SIMILARITY_PATTERN` — features that make historical cases useful comparators without implying same cause.

## A learning is not created from one anecdote by default

One incident may create a candidate learning, but not necessarily an established memory.

Example:

```text
Incident 1:
worker restart reduced queue latency
```

This supports:

```text
candidate:
"worker restart may temporarily reduce queue latency"
```

It does not justify:

```text
"worker restart fixes queue latency incidents"
```

Repeated independent observations, correct scope, and contradictory cases matter.

## Scope is mandatory

Every memory record must state where it applies.

Possible scope dimensions:

- repository / subsystem
- service / capability
- environment
- language / framework
- dependency / provider
- change shape
- incident class
- revision range
- time range
- deployment topology
- tenant / region

A memory that was true for one Rails monolith must not silently become universal software wisdom.

## Supporting and contradicting cases

A memory record keeps references to both:

```text
supporting_case_refs
contradicting_case_refs
```

Contradictory evidence does not disappear. It may:

- weaken the memory;
- narrow its scope;
- split one memory into multiple scoped memories;
- mark it `CONFLICTED`;
- supersede it.

## Applicability is separate from truth

A learning can be well established historically and still be inapplicable now.

Example:

```text
Memory:
"Restarting Sidekiq workers clears stuck jobs caused by middleware bug X"

Current system:
middleware bug X was removed six months ago
```

The memory may remain historically true but have low current applicability.

Therefore future reasoning should evaluate:

```text
memory validity
× scope match
× freshness
× identity continuity
× current applicability
```

## Freshness and decay

Not all memory should decay the same way.

- A code pattern tied to a pinned revision does not decay within that revision.
- Current ownership knowledge can become stale quickly.
- Vendor/API behavior may change externally.
- Remediation effectiveness can change after architecture migrations.
- A mathematical or protocol invariant may not decay at all unless assumptions change.

Decay should therefore be rule-based and memory-kind-specific, not a universal time constant.

## Reinforcement

When a new case is compatible with an existing memory:

```text
new case
  ↓
match candidate memory
  ↓
validate scope compatibility
  ↓
append support
  ↓
recompute belief / applicability
```

Do not silently rewrite the original record.

## Weakening and supersession

When a new observation contradicts a memory:

```text
memory M1
  ↓
new contradicting case
  ↓
M1 weakened / conflicted
  ↓
optional M2 with narrower or corrected scope
```

Historical consumers must still be able to ask what the system believed before the correction.

## Calibration memory

Prediction history deserves its own learning path.

For a prediction family, retain:

```text
predictions_made
confirmed
partially_confirmed
contradicted
inconclusive
not_observed
```

This can calibrate future prediction confidence.

For example:

```text
pattern:
"changes to retry semantics may duplicate payment capture"

historical predictions: 18
materialized: 5
false positives: 2
insufficient follow-up: 4
```

The system should not turn this blindly into a probability unless the sample and sampling process justify it, but it should use the history to improve confidence and prioritization.

## Diagnostic value

Engineering memory should learn not only what happened, but what evidence was useful.

Example:

```text
Incident class:
duplicate payment behavior

Verification A:
source inspection
median discrimination time: 28 min

Verification B:
trace correlation by idempotency key
median discrimination time: 4 min
```

Future planners can prefer B first.

This creates a learning loop for Evidence Planner itself.

## Remediation effectiveness

Actions must be learned from outcomes, not command success.

```text
Action:
restart worker

execution:
SUCCEEDED

engineering outcome:
INEFFECTIVE
```

The memory should learn the second fact, not merely the first.

Useful dimensions:

- action kind
- target / scope
- preconditions
- reversibility
- execution success
- engineering outcome
- time to mitigation
- recurrence after action
- side effects

## Negative memory matters

Useful engineering memory includes failed approaches:

```text
"Restarting the API repeatedly masked the symptom and delayed diagnosis."
```

or:

```text
"File-name similarity is not reliable identity evidence after repository split."
```

These anti-patterns can prevent repeated wasted work.

## Memory retrieval

Retrieval should be evidence-aware and scope-aware.

A useful retrieval ranking can consider:

```text
entity identity match
change-shape match
incident/finding class match
environment match
architecture epoch match
freshness
support strength
contradictions
historical usefulness
```

Semantic similarity alone is insufficient.

## Memory projections

The same learning can appear differently by product surface.

### PR X-Ray

```text
"Similar retry changes previously materialized as duplicate capture risk in 3 incidents."
```

### Operational

```text
"This symptom pattern previously responded poorly to worker restarts; trace correlation was the fastest discriminator."
```

### Incident view

```text
"Two historical incidents match the current evidence shape, but only one shares the same deployment topology."
```

### Overviewable

```text
"Architecture ownership for this component has drifted repeatedly after team transfers."
```

## Memory states

Suggested lifecycle:

- `CANDIDATE`
- `SUPPORTED`
- `ESTABLISHED`
- `WEAKENED`
- `CONFLICTED`
- `STALE`
- `SUPERSEDED`
- `RETRACTED`

A memory state describes the learning record, not current applicability.

## Never learn silently from model prose

A model-generated summary is not itself sufficient evidence.

A candidate memory must reference underlying artifacts such as:

- assertions
- findings
- risks
- predictions
- incidents
- verifications
- actions
- outcomes
- conflicts
- evidence

The model may propose a learning. Machine-owned records preserve the evidence chain.

## Human correction

Humans may:

- confirm a candidate;
- narrow scope;
- reject a false pattern;
- explain an exception;
- mark a memory obsolete;
- add policy context.

Corrections should create auditable state changes, not overwrite history invisibly.

## Invariants

1. Raw history is not engineering memory.
2. Every memory has provenance.
3. Scope is mandatory.
4. Support and contradiction are both retained.
5. Historical truth and current applicability are separate.
6. Memory can weaken, conflict, stale, and be superseded.
7. One anecdote does not automatically become a general rule.
8. Semantic similarity alone cannot establish applicability.
9. Action execution success cannot stand in for remediation effectiveness.
10. Predictions must be calibrated against observed outcomes.
11. Memory should improve future evidence planning, not merely answer retrospective questions.
12. Model prose may propose memories but cannot establish them without evidence.

## Closed learning loop

```text
observe
  ↓
model world
  ↓
predict / decide / act
  ↓
observe outcome
  ↓
compare expectation vs reality
  ↓
extract candidate learning
  ↓
validate / scope / store
  ↓
retrieve in future reasoning
  ↓
measure whether it improved the next decision
```

The final step matters: a memory system should itself be evaluated by whether its retrieved lessons improve decisions, reduce unnecessary evidence acquisition, shorten diagnosis, or improve prediction calibration.

## Compact thesis

> The system should remember validated lessons, not merely previous text.

And:

> Engineering memory is evidence-backed, scoped, revisable learning that changes how future evidence is gathered and interpreted.
