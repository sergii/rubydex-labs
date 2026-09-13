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

## Recorded result

The final recorded run used 12 frozen natural-language requests, three independent H classifications per request, and the oracle condition O as an upper-bound control.

| Metric | H — natural-language classifier | O — oracle |
| --- | ---: | ---: |
| Classification correct | **36/36** | 36/36 |
| Route correct | **36/36** | 36/36 |
| Executed downstream tasks | 24 | 24 |
| Downstream exact | **23/24** | **24/24** |
| Observed backend route | **24/24** | **24/24** |

Classifier medians were roughly 1.4–1.7 seconds and about 500 tokens per request across all four evidence classes. The classifier cost was negligible relative to the downstream agent.

The full recorded report is in [`../../benchmarks/results/2026-09-13-lab-10-natural-language-evidence-routing.md`](../../benchmarks/results/2026-09-13-lab-10-natural-language-evidence-routing.md).

## Interpretation

The frozen corpus supports a narrow but useful claim:

> The four-way evidence taxonomy is learnable from ordinary engineering language, and an explicit low-cost classifier can reproduce the oracle evidence route on this benchmark.

This does **not** mean evidence routing is universally solved. The 12 unique requests are intentionally well separated and repeated three times.

The result strengthens the architecture introduced by Labs 08–09: evidence selection should be an explicit product layer rather than either `semantic-first everywhere` or unconstrained model tool choice.

## The completeness lesson

The single H downstream miss is especially important.

For `semantic-02-H-r3`, routing was correct and Rubydex returned the complete direct-reference evidence, including the production `DiscourseSolved::Categories::Types::Support` reference. The model then omitted that item while converting the tool output into its final answer.

So the failure occurred **after** correct evidence acquisition.

That gives us a new invariant:

```text
Models may interpret evidence.
Models must not reconstruct authoritative complete sets
when a deterministic backend can preserve them.
```

Queries containing semantics like `all`, `every`, `complete set`, or otherwise completeness-sensitive membership should flow through a machine-owned `EvidenceSet`: membership, count, filtering, scope, and provenance are preserved deterministically, while the model explains consequences on top.

See [`../../docs/evidence-architecture.md`](../../docs/evidence-architecture.md) and [`../../schemas/evidence-set.schema.json`](../../schemas/evidence-set.schema.json).

## From EvidenceRoute to EvidencePlan

Lab 10 intentionally chooses exactly one evidence class. Real engineering questions often need several.

For example, "Is this checkout change safe in production?" may require:

```text
SEMANTIC_RELATIONSHIP_SET   required
ARCHITECTURE_KNOWLEDGE      required
RUNTIME_BEHAVIOR            required
SOURCE_LOCAL                optional
```

The next architectural abstraction is therefore an `EvidencePlan`: a small DAG describing which evidence backends are required, which are optional, and what depends on what.

The draft contract lives at [`../../schemas/evidence-plan.schema.json`](../../schemas/evidence-plan.schema.json).

## Limitations

- The corpus has 12 unique requests; 36/36 classification is a benchmark result, not a universal production accuracy claim.
- Runtime and architecture routes are classification-only in this lab because their backends are not wired into the repository yet.
- Source and semantic tasks reuse the frozen Lab 07 ground truth to isolate routing quality.
- H and O downstream differences can still contain normal model variance once both routes reach the same backend.
- The current classifier is single-label; multi-backend evidence planning remains future work.
