# Lab 03 result - Discovery scaling, large

Date: 2026-09-12

## Scenario

Discovery-only benchmark at the `large` fixture size.

- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Execution: sequential A -> B
- Noise domains: 150
- Approximate extra Ruby files: 450
- Ground truth: seven references to `Inventory::Reservation`

The pair runner executed the text-only condition first and started the Rubydex condition only after A completed, avoiding local CPU contention between conditions.

## Result

Both conditions returned all seven target references with no target-reference recall loss.

| Metric | A - text | B - Rubydex | B vs A |
| --- | ---: | ---: | ---: |
| Reference recall | 7/7 | 7/7 | equal |
| Elapsed seconds | 45 | 35 | -22.2% |
| Total tokens | 181,994 | 97,914 | -46.2% |
| Input tokens | 180,301 | 96,714 | -46.4% |
| Cached input tokens | 146,944 | 75,264 | -48.8% |
| Uncached input tokens | 33,357 | 21,450 | -35.7% |
| Output tokens | 1,693 | 1,200 | -29.1% |
| Reasoning output tokens | 617 | 602 | -2.4% |

## Interpretation

At this scale, semantic reference resolution is no longer merely a correctness aid or a token optimization. It wins on both measured cost and latency while preserving perfect recall.

The strongest signal is context reduction. The Rubydex condition used 46.4% fewer input tokens overall and 35.7% fewer uncached input tokens. That is consistent with the intended mechanism: the semantic graph identifies the exact declaration and resolved references so the agent does not need to inspect and reason through hundreds of plausible text-search candidates.

The 22.2% wall-clock improvement is also more credible than earlier latency measurements because A and B ran sequentially instead of competing for local CPU.

The reasoning-token difference is small (-2.4%). The gain therefore appears to come primarily from reducing code/context acquisition rather than dramatically reducing the model's internal reasoning effort.

## Relation to the medium Luna run

The clean `medium` Luna pair also preserved 7/7 recall and showed a Rubydex advantage:

- elapsed time: 39 s -> 34 s (-12.8%)
- total tokens: 182,828 -> 136,346 (-25.4%)
- input tokens: 181,353 -> 135,285 (-25.4%)
- uncached input tokens: 50,025 -> 21,109 (-57.8%)

The large run strengthens the direction of the result: as repository ambiguity increased, the total-token advantage widened from roughly 25% to 46%, and the wall-clock advantage widened from roughly 13% to 22% in these samples.

This is still a benchmark sample rather than a universal performance claim. Repeated runs and different task shapes would be needed to estimate variance and generalize beyond this fixture.

## Current conclusion

For exact constant-reference discovery in a noisy Ruby codebase:

- tiny fixtures do not justify assuming a Rubydex win
- medium fixtures show a meaningful context-cost advantage
- large fixtures show a strong context-cost advantage and a measurable latency advantage

The experiment therefore provides evidence for a practical crossover: semantic navigation becomes increasingly valuable as the number of same-named or textually plausible candidates grows.
