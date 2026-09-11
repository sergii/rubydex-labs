# Lab 03 result - Discovery scaling, medium, first run

Date: 2026-09-12

## Scenario

Discovery-only benchmark. No editing, Rails boot, or tests.

The base fixture was expanded with 40 independent noise namespaces. Each noise namespace contributes:

- its own `Reservation` class
- a `PriorityReservation < Reservation`
- two unqualified `Reservation` references in a consumer
- a string literal containing `"Inventory::Reservation"`

This adds 120 Ruby files designed to be plausible text-search candidates while remaining separate semantic declarations.

Both conditions correctly identified the same seven references to `Inventory::Reservation`:

```text
app/jobs/inventory/reservation_sync_job.rb:4
app/jobs/inventory/reservation_sync_job.rb:8
app/models/inventory/priority_reservation.rb:2
app/services/inventory/allocator.rb:4
app/services/inventory/allocator.rb:8
app/services/orders/processor.rb:4
app/services/orders/processor.rb:8
```

Both also correctly separated `Admin::Reservation` and the 40 `NoiseDomainNNNN::Reservation` declarations.

## Run A - text navigation

Condition: no Rubydex project tool or Rubydex MCP.

Observed behavior:

- listed Ruby files
- broadly searched for `Reservation` and `Inventory`
- inspected the generated noise-domain files
- reasoned from explicit qualification and lexical module nesting
- returned all seven target references correctly

Metrics:

```text
Elapsed runner time: 57 s
Total tokens: 29,365
Input tokens: 28,031
Output tokens: 1,334
Cached input: 97,280
Correct references: 7/7
Edits: none
```

## Run B - Rubydex semantic-first

Condition: Rubydex MCP enabled and the prompt required semantic discovery before broad text search.

Observed behavior:

- `get_declaration(Inventory::Reservation)` resolved the target immediately
- `find_constant_references(Inventory::Reservation)` returned exactly seven references
- narrow source reads verified the returned locations
- additional `search_declarations(Reservation)` calls enumerated same-named declarations
- `Admin::Reservation` was checked separately
- returned all seven target references correctly

Metrics:

```text
Elapsed runner time: 96 s
Codex reported work time: 79 s
Total tokens: 18,655
Input tokens: 17,674
Output tokens: 981
Cached input: 129,280
Correct references: 7/7
Edits: none
```

## Comparison

| Metric | A - text | B - Rubydex | Difference |
| --- | ---: | ---: | ---: |
| Correct references | 7/7 | 7/7 | equal |
| Total tokens | 29,365 | 18,655 | Rubydex -36.5% |
| Input tokens | 28,031 | 17,674 | Rubydex -36.9% |
| Output tokens | 1,334 | 981 | Rubydex -26.5% |
| Runner wall-clock | 57 s | 96 s | Rubydex +68.4% |

## Interpretation

This is the first run where Rubydex shows a clear resource advantage: semantic navigation reduced total token use by roughly 36.5% while preserving perfect reference accuracy.

The wall-clock comparison is **not valid yet**. During Run B, Codex repeatedly requested user approval, while Run A did not. The runner included those pauses in its 96-second measurement. Global unrelated MCP servers also emitted startup/authentication warnings. Therefore this run is useful for token/context comparison but not for latency comparison.

The Rubydex agent also spent avoidable work enumerating all declarations named `Reservation` after it already had the exact resolved reference set. That operation was not necessary to answer the task and should be treated as agent-strategy overhead rather than Rubydex requirements.

## Runner correction

Subsequent discovery runs pin:

```text
approval_policy = never
sandbox_mode = read-only
```

because Lab 03 is intentionally read-only. This removes human approval latency from the timed region while keeping the agent unable to modify the fixture.

## Current signal

At medium scale:

- accuracy: tie
- token/context efficiency: Rubydex clearly wins on this run
- latency: inconclusive because of approval contamination

The next useful experiment is a repeated medium run under the corrected non-interactive runner, followed by the large fixture if the token advantage persists.
