# Lab 04 result - Real Discourse codebase

Date: 2026-09-12

## Scenario

Real production Rails monolith benchmark on a pinned Discourse revision.

- Repository: `discourse/discourse`
- Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Target declaration: `Categories::Types::Base`
- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Frozen semantic ground truth: 21 constant references
- Rubydex scout graph: 15,130 files, 137,534 declarations, 145,449 definitions, 453,208 constant references, 1,559,344 method references
- Textual ambiguity observed by scout: 2,574 visible exact-name declaration matches for `Base`

The benchmark ran twice with counterbalanced execution order:

1. `AB`: text navigation first, Rubydex second
2. `BA`: Rubydex first, text navigation second

Both conditions were read-only and discovery-only. Rubydex MCP startup/indexing remained inside B's measured session time.

## Correctness scoring correction

The first scoring implementation treated every path-looking substring in explanatory prose as an answer reference. In the `AB` run this incorrectly classified shortened prose mentions such as `discussion.rb:5`, `categories_controller.rb:616`, and `base.rb:158` as false positives.

Manual inspection of the final answers shows that both A and B returned the same 21 full repository-relative `path:line` entries as the frozen ground truth. The `BA` run was already scored exact for both conditions.

The harness now scores only standalone `path:line` answer entries. Under that corrected rule:

| Run | A - text | B - Rubydex |
| --- | --- | --- |
| `AB` | 21/21, 100% precision, exact | 21/21, 100% precision, exact |
| `BA` | 21/21, 100% precision, exact | 21/21, 100% precision, exact |

## AB result

| Metric | A - text | B - Rubydex | B vs A |
| --- | ---: | ---: | ---: |
| Elapsed seconds | 55 | 39 | -29.1% |
| Total tokens | 214,174 | 92,412 | -56.9% |
| Input tokens | 211,941 | 90,838 | -57.1% |
| Cached input tokens | 167,424 | 76,544 | -54.3% |
| Uncached input tokens | 44,517 | 14,294 | -67.9% |
| Output tokens | 2,233 | 1,574 | -29.5% |
| Reasoning output tokens | 993 | 616 | -38.0% |

## BA result

| Metric | A - text | B - Rubydex | B vs A |
| --- | ---: | ---: | ---: |
| Elapsed seconds | 58 | 40 | -31.0% |
| Total tokens | 180,155 | 91,636 | -49.1% |
| Input tokens | 177,712 | 90,135 | -49.3% |
| Cached input tokens | 146,944 | 76,544 | -47.9% |
| Uncached input tokens | 30,768 | 13,591 | -55.8% |
| Output tokens | 2,443 | 1,501 | -38.6% |
| Reasoning output tokens | 1,183 | 691 | -41.6% |

## Counterbalanced interpretation

The Rubydex advantage survived the order reversal.

Across the two runs, B's observed advantage stayed within these ranges:

- elapsed time: 29.1% to 31.0% lower
- total tokens: 49.1% to 56.9% lower
- input tokens: 49.3% to 57.1% lower
- uncached input tokens: 55.8% to 67.9% lower
- output tokens: 29.5% to 38.6% lower
- reasoning output tokens: 38.0% to 41.6% lower

Descriptive two-run averages were:

| Metric | A average | B average | B vs A |
| --- | ---: | ---: | ---: |
| Elapsed seconds | 56.5 | 39.5 | -30.1% |
| Total tokens | 197,164.5 | 92,024.0 | -53.3% |
| Input tokens | 194,826.5 | 90,486.5 | -53.6% |
| Cached input tokens | 157,184.0 | 76,544.0 | -51.3% |
| Uncached input tokens | 37,642.5 | 13,942.5 | -63.0% |
| Output tokens | 2,338.0 | 1,537.5 | -34.2% |
| Reasoning output tokens | 1,088.0 | 653.5 | -39.9% |

These averages are descriptive only; two runs are not enough for a statistical estimate of variance.

## Stability signal

B was notably stable across execution order:

- elapsed: 39 s vs 40 s
- total tokens: 92,412 vs 91,636
- uncached input: 14,294 vs 13,591

A varied more between runs:

- elapsed: 55 s vs 58 s
- total tokens: 214,174 vs 180,155
- uncached input: 44,517 vs 30,768

That pattern is consistent with semantic-first navigation constraining the agent's search path, while text-first navigation leaves more room for stochastic exploration.

## Conclusion

On this pinned real Discourse codebase and this exact constant-reference discovery task, Rubydex preserved exact correctness while substantially reducing both context acquisition and end-to-end session time.

The result is stronger than the synthetic Lab 03 result because:

- the codebase is a real actively maintained Rails monolith
- the target has real lexical and namespace ambiguity
- the benchmark includes core code, plugins, and specs
- the semantic index cost is included in B's timing
- the result survives `AB` / `BA` counterbalancing

This still does not establish a universal speedup for every Rails task. The demonstrated claim is narrower: for exact Ruby constant-reference discovery in a large ambiguous Rails repository, semantic navigation can materially reduce agent context cost and latency without sacrificing correctness.
