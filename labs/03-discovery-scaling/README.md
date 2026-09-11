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

Start with medium:

```bash
bin/run-discovery-a medium
bin/run-discovery-b medium
```

Then repeat at other scales only if useful:

```bash
bin/run-discovery-a small
bin/run-discovery-b small

bin/run-discovery-a large
bin/run-discovery-b large
```

Use fresh Codex sessions. Keep the same model and effort level for A and B.

## Metrics

Record:

- correctness / recall of the seven real references
- false positives in the final answer
- wall-clock time
- token usage
- search/tool calls
- files inspected
- whether the agent had the complete correct dependency set before source reads

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