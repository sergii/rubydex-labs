# Lab 03 - Discovery scaling

## Question

At what repository ambiguity does semantic reference resolution become cheaper than text search plus agent reasoning?

Lab 02 mixed navigation, editing, Rails boot, runtime assertions, diff review, and cleanup. Those later phases dominated the end-to-end result. Lab 03 isolates the capability Rubydex is intended to improve: finding the exact references to one Ruby declaration in a noisy codebase.

## Task

The agent must identify every Ruby constant reference that resolves to `Inventory::Reservation` and return exact `path:line` locations.

It must also distinguish unrelated declarations named `Reservation`.

The agent must not edit files, run Rails, or run tests.

## Conditions

### A - text navigation

Rubydex is removed from the fixture. The agent may use file listing, `rg`, `grep`, and source reads.

### B - semantic-first

Rubydex MCP is available. Before broad text search or reading candidate source files, the agent must resolve `Inventory::Reservation` and query its resolved constant references.

## Scale

The fixture generator adds deterministic unrelated `Reservation` declarations, references, inheritance, and textual strings.

| Size | Noise domains | Approx extra Ruby files |
| --- | ---: | ---: |
| `small` | 0 | 0 |
| `medium` | 40 | 120 |
| `large` | 150 | 450 |

Each noise domain contains:

- its own `Reservation` declaration
- unqualified references that resolve to that declaration
- a subclass inheriting from that declaration
- prose/history strings containing `Inventory::Reservation`

The real target remains the same seven references from Lab 02.

## Run

Single conditions can be started headlessly:

```bash
bin/run-discovery-a medium
bin/run-discovery-b medium
```

Check them with:

```bash
bin/discovery-status A medium
bin/discovery-status B medium
```

For a clean latency comparison, prefer the sequential pair runner. It runs A to completion, then B, and builds a comparison automatically:

```bash
bin/run-discovery-pair large
bin/discovery-pair-status large
```

The pair runner records JSONL Codex events, final answers, token usage, exact run directories, ground-truth reference recall, and a Markdown/JSON comparison.

The benchmark currently defaults to:

```text
model = gpt-5.6-luna
reasoning = medium
```

A and B use isolated temporary `CODEX_HOME` directories so unrelated MCP servers, hooks, and global Codex configuration do not affect the experiment.

## Metrics

Record:

- correctness / recall of the seven real references
- false positives in the final answer
- wall-clock time
- total input and output tokens
- cached and uncached input tokens
- reasoning output tokens
- search/tool calls
- files inspected
- whether the agent had the complete correct dependency set before source reads

## Observed crossover

The clean Luna runs show the expected scaling effect.

| Scale | Correctness | Time A -> B | Total tokens A -> B | Uncached input A -> B |
| --- | --- | --- | --- | --- |
| `medium` | 7/7 vs 7/7 | 39 s -> 34 s (-12.8%) | 182,828 -> 136,346 (-25.4%) | 50,025 -> 21,109 (-57.8%) |
| `large` | 7/7 vs 7/7 | 45 s -> 35 s (-22.2%) | 181,994 -> 97,914 (-46.2%) | 33,357 -> 21,450 (-35.7%) |

The medium timing came from overlapping A/B processes, so treat its latency delta as directional. The large pair ran sequentially and is the cleaner latency comparison.

At `large`, Rubydex preserved perfect recall while using 46.2% fewer total tokens and finishing 22.2% faster. The reasoning-token difference was only 2.4%, suggesting the main gain came from reducing code/context acquisition rather than eliminating model reasoning.

See:

- [`benchmarks/results/2026-09-12-lab-03-discovery-medium-first-run.md`](../../benchmarks/results/2026-09-12-lab-03-discovery-medium-first-run.md)
- [`benchmarks/results/2026-09-12-lab-03-discovery-large-luna.md`](../../benchmarks/results/2026-09-12-lab-03-discovery-large-luna.md)

## Interpretation

The experiment supports a practical crossover rather than a universal Rubydex win:

```text
tiny codebase / low ambiguity
    text search is cheap; semantic setup may not pay back

medium ambiguity
    semantic navigation begins reducing context cost materially

large ambiguity
    semantic navigation reduces both context cost and end-to-end latency
```

The mechanism is straightforward: text search returns plausible lexical matches and leaves identity resolution to the agent, while Rubydex returns references already bound to the exact Ruby declaration. As same-named declarations and textual noise increase, the amount of irrelevant context the text-navigation agent must inspect grows faster than the semantic query result.

These are benchmark samples, not universal performance claims. Repetitions, other Ruby constructs, and real production repositories are the next step before generalizing the percentages.

## Ground truth

Do not expose this section to the benchmark agent.

The target has exactly seven constant references across four referencing files:

- `app/models/inventory/priority_reservation.rb:2`
- `app/services/inventory/allocator.rb:4`
- `app/services/inventory/allocator.rb:8`
- `app/services/orders/processor.rb:4`
- `app/services/orders/processor.rb:8`
- `app/jobs/inventory/reservation_sync_job.rb:4`
- `app/jobs/inventory/reservation_sync_job.rb:8`

The declaration itself is not counted as a reference.
