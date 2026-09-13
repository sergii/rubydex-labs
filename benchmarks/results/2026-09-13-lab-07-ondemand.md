# Lab 07 - Rubydex on-demand benchmark

Date: 2026-09-13

GitHub Actions run: https://github.com/sergii/rubydex-labs/actions/runs/34764721882

Model: `gpt-5.6-luna`
Reasoning: `medium`
Samples: 3 per condition, each on a fresh GitHub-hosted VM

## Conditions

- D - source + explicit architecture knowledge + targeted semantic-impact skill
- E - identical source + knowledge + skill, with Rubydex MCP available but optional

The prompt did not mention or require Rubydex. The purpose was to test whether the agent would autonomously choose semantic tooling when faced with inheritance, an alias, a reopened class, and lexical decoys.

## Aggregate result

| Condition | Impact recall | Risk recall | Verification recall | Policy recall | Consequence exact | Knowledge exact | Median time | Median tokens | Median est. cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D - knowledge | 100.0% | 100.0% | 100.0% | 0.0% | 0/3 | 1/3 | 15.3 s | 33,031 | $0.0041 |
| E - knowledge + optional Rubydex | 100.0% | 100.0% | 100.0% | 100.0% | 0/3 | 2/3 | 19.6 s | 35,533 | $0.0041 |

## Critical tool-use finding

Inspection of all three E job logs showed **zero Rubydex/MCP tool calls**.

Every E sample solved the structural trace with ordinary source inspection, primarily `rg --files` and `sed`. In other words, Rubydex was configured and available but the agent never chose to invoke it.

Therefore the apparent E advantage in median policy recall **must not be attributed to Rubydex**. It is compatible with normal run-to-run model variance or other incidental context differences.

This is the central result of Lab 07: making semantic tooling available is not sufficient to make an agent use it when the repository is small enough to scan directly.

## Exact-score caveat

Both D and E had `consequence_exact = 0/3` despite 100% median recall. The dominant issue was precision/selection variance, especially around whether `IMPACT-STRIPE` should count as an impacted surface when the provider charge still executes but its post-capture hook is removed. One E sample also omitted `IMPACT-PAYMENT-CAPTURE`.

This means the closed ground-truth vocabulary is useful for deterministic scoring, but this fixture exposes an ambiguity in the definition of "impact" versus "still-executing dependency." Future cases should define that boundary more sharply or score direct/behavioral/downstream impacts separately.

## What the experiment supports

1. Architecture knowledge and a targeted reasoning skill remain sufficient to recover the important business consequences in this small fixture.
2. Optional Rubydex did not create measurable semantic-tool value because the agent never used it.
3. A ten-file fixture is still too cheap to scan wholesale. The agent can read the entire relevant source tree in one or two shell commands, so there is little economic reason for it to reach for a semantic index.
4. The question for the next benchmark is not merely whether Rubydex is available, but whether a semantic query becomes cheaper and more reliable than source traversal at realistic repository scale.

## Next experiment

Use a substantially larger or real repository and measure actual tool-selection behavior.

Recommended conditions:

```text
D = source + knowledge
E = source + knowledge + Rubydex optional
F = source + knowledge + Rubydex optional + a minimal decision rule:
    use semantic evidence only when structural uncertainty remains;
    do not call it merely because it exists
```

Add metrics for:

- Rubydex tool-call count;
- which semantic tools were called;
- source files read;
- shell/search commands;
- correctness and unsupported claims;
- total tokens, uncached input, latency, and cost.

The next fixture should contain enough files, similarly named constants, inheritance depth, reopenings, aliases, indirect references, and unrelated lexical matches that reading the whole repository is no longer the obvious cheapest strategy. A real-codebase task such as the existing Discourse labs is preferable to adding more complexity to a tiny synthetic fixture.

## Product implication

The current evidence does not support `semantic-first everywhere`, and it also does not yet show that agents will naturally discover when to use a semantic graph.

A more defensible design principle is:

> Keep semantic tooling available as deterministic evidence, but make the cost/benefit of using it observable and test tool-selection behavior at realistic repository scale.
