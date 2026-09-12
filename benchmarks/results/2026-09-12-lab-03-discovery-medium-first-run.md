# Lab 03 result - Discovery scaling, medium

Date: 2026-09-12

## Scenario

Discovery-only benchmark. No editing, Rails boot, or tests.

The base fixture was expanded with 40 independent noise namespaces. Each noise namespace contributes:

- its own `Reservation` class
- a `PriorityReservation < Reservation`
- two unqualified `Reservation` references in a consumer
- a string literal containing `"Inventory::Reservation"`

This adds 120 Ruby files designed to be plausible text-search candidates while remaining separate semantic declarations.

The ground-truth references are:

```text
app/jobs/inventory/reservation_sync_job.rb:4
app/jobs/inventory/reservation_sync_job.rb:8
app/models/inventory/priority_reservation.rb:2
app/services/inventory/allocator.rb:4
app/services/inventory/allocator.rb:8
app/services/orders/processor.rb:4
app/services/orders/processor.rb:8
```

## Earlier Astra/xhigh exploration

The first interactive experiments used `gpt-6-astra` with `xhigh` reasoning. They established that both text navigation and Rubydex could reach 7/7 correctness, but several runs were contaminated by interactive approval pauses, unrelated MCP startup state, or runner configuration failures.

A valid early pair showed a substantial token reduction for Rubydex but unusable latency comparison:

| Metric | A - text | B - Rubydex |
| --- | ---: | ---: |
| Correct references | 7/7 | 7/7 |
| Interactive reported total tokens | 29,365 | 18,655 |
| Runner wall-clock | 57 s | 96 s, approval-contaminated |

A second valid text-only run returned 7/7 in 86 s with 25,686 interactive reported tokens. Invalid semantic attempts caused by approval policy, malformed global MCP configuration, prompt transport, and usage limits are not benchmark results.

These Astra results are retained as exploratory history only and are not directly mixed with the Luna benchmark below.

## Clean headless benchmark - GPT-5.6 Luna / medium

The runner was then converted to isolated, non-interactive `codex exec --json` runs with:

```text
model = gpt-5.6-luna
model_reasoning_effort = medium
approval_policy = never
sandbox_mode = read-only
```

Semantic runs expose only the project-local Rubydex MCP server. User MCP servers, hooks, and global Codex configuration are excluded through a per-run `CODEX_HOME`.

Both runs completed successfully and returned exactly the seven ground-truth references.

### A - text navigation

```text
Elapsed: 39 s
Input tokens: 181,353
Cached input tokens: 131,328
Uncached input tokens: 50,025
Output tokens: 1,475
Reasoning output tokens: 542
Total tokens: 182,828
Correct references: 7/7
```

The agent separated `Inventory::Reservation` from `Admin::Reservation`, the 40 generated `NoiseDomainNNNN::Reservation` constants, string literals, and the target declaration itself.

### B - Rubydex semantic-first

```text
Elapsed: 34 s
Input tokens: 135,285
Cached input tokens: 114,176
Uncached input tokens: 21,109
Output tokens: 1,061
Reasoning output tokens: 472
Total tokens: 136,346
Correct references: 7/7
```

Rubydex resolved the target declaration and the exact seven semantic references. The final answer explicitly excluded `Admin::Reservation` and generated noise-domain constants because they resolve to different fully qualified declarations.

### Clean-pair comparison

| Metric | A - text | B - Rubydex | Rubydex delta |
| --- | ---: | ---: | ---: |
| Correct references | 7/7 | 7/7 | equal |
| Wall-clock | 39 s | 34 s | **-12.8%** |
| Total tokens | 182,828 | 136,346 | **-25.4%** |
| Input tokens | 181,353 | 135,285 | **-25.4%** |
| Cached input tokens | 131,328 | 114,176 | **-13.1%** |
| Uncached input tokens | 50,025 | 21,109 | **-57.8%** |
| Output tokens | 1,475 | 1,061 | **-28.1%** |
| Reasoning output tokens | 542 | 472 | **-12.9%** |

`codex exec --json` reports `cached_input_tokens` as a subset of `input_tokens`, so `uncached_input_tokens = input_tokens - cached_input_tokens`. The headless `total_tokens` above is `input_tokens + output_tokens` and should not be compared numerically with the earlier interactive CLI's displayed token totals, which presented cached tokens separately.

## Interpretation

This is the first clean medium-scale pair where Rubydex wins on all primary dimensions we care about while preserving correctness:

- same semantic recall: 7/7 references
- lower wall-clock latency in this pair
- roughly one quarter fewer total/input tokens
- less than half as much uncached input
- less output and reasoning work

The strongest signal is the **57.8% reduction in uncached input**. Text navigation had to ingest and reason over substantially more novel repository content, while Rubydex reduced the problem to a small semantic neighborhood.

The wall-clock result should still be treated as one sample. A and B were launched about ten seconds apart and overlapped for part of their execution, so local CPU/process contention is possible. Token counts are not affected by that caveat.

## Current conclusion

At the 40-noise-domain / 120-extra-file medium fixture, semantic navigation has crossed from merely providing deterministic evidence to showing a measurable efficiency advantage for GPT-5.6 Luna.

The next useful experiment is `large` with 150 noise domains / 450 extra Ruby files, preferably running A and B sequentially in one background pair so latency is not affected by concurrent local work.