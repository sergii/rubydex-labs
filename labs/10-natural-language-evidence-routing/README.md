# Lab 10 — natural-language evidence routing

## Goal

Remove the oracle scenario label from Lab 09 and test whether a small classifier can recover the correct evidence class from an ordinary engineering request before the main coding agent starts.

The production-shaped pipeline under test is:

```text
raw engineering request
        |
        v
 evidence classifier
        |
        v
 evidence router
   /      |       |       \
source semantic runtime architecture
   \      /        |       /
    routed evidence backend
             |
             v
            agent
```

Lab 09 proved the value of correct routing once task shape was already known. Lab 10 tests the missing step: infer that route from natural language.

## Evidence classes

```text
SOURCE_LOCAL
SEMANTIC_RELATIONSHIP_SET
RUNTIME_BEHAVIOR
ARCHITECTURE_KNOWLEDGE
```

- `SOURCE_LOCAL` — a local declaration/file/method answer that does not require repository-wide enumeration.
- `SEMANTIC_RELATIONSHIP_SET` — complete resolved descendants, references, reopenings, extensions, or other repository-wide semantic relationship sets.
- `RUNTIME_BEHAVIOR` — observed execution evidence such as traces, latency, retries, errors, query counts, or production behavior.
- `ARCHITECTURE_KNOWLEDGE` — declared boundaries, ownership, business capabilities/flows, policies, or other system knowledge not recoverable from code structure alone.

## Conditions

```text
H = classifier sees only the raw request and selects the evidence class
O = oracle uses the hidden expected class
```

`O` is an upper-bound control, not a production implementation.

For tasks classified as `SOURCE_LOCAL` or `SEMANTIC_RELATIONSHIP_SET`, the selected route is executed against the same pinned Discourse fixture and frozen structural ground truth used by Labs 07–09. The downstream task is normalized to the existing benchmark contract so the experiment isolates routing quality rather than output-format variance.

`RUNTIME_BEHAVIOR` and `ARCHITECTURE_KNOWLEDGE` requests are classification-only in this lab. The repository does not pretend that Rubydex or source navigation can answer runtime/architecture questions. Future labs can attach OpenTelemetry/runtime and architecture-knowledge backends to those routes.

## Request set

The frozen request corpus lives in [`requests.json`](requests.json). It includes:

- three local source requests;
- five semantic relationship-set requests;
- two runtime requests;
- two architecture-knowledge requests.

The classifier prompt contains class definitions and tie-breaking rules but no benchmark examples or expected labels.

## Measurements

Classifier layer:

- class accuracy overall and per evidence class;
- classifier latency;
- classifier input/output/total tokens;
- estimated classifier API cost.

End-to-end executable layer:

- selected route versus hidden oracle route;
- actual Rubydex use versus routed path;
- exact downstream correctness against frozen ground truth;
- downstream latency/tokens/cost;
- combined classifier + agent cost.

A classifier mistake that routes an executable source/semantic task to runtime/architecture counts as a downstream failure because the main agent is intentionally not run with a fabricated backend.

## Hypothesis

A small explicit classifier should recover most or all of the Lab 09 oracle routing decisions at a tiny fraction of the downstream cost. If it does, evidence selection can become a deterministic product layer instead of an implicit prompt habit.

The key metric is not "Rubydex usage." It is **correct evidence-path selection at the lowest reliable cost**.
