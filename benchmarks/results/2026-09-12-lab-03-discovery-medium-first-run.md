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

## First pair

### Run A - text navigation

```text
Elapsed runner time: 57 s
Total tokens: 29,365
Input tokens: 28,031
Output tokens: 1,334
Cached input: 97,280
Correct references: 7/7
Edits: none
```

### Run B - Rubydex semantic-first

Rubydex immediately resolved the target and returned exactly seven references. The agent then performed narrow verification and some unnecessary same-name declaration enumeration.

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

### First-pair comparison

| Metric | A - text | B - Rubydex | Difference |
| --- | ---: | ---: | ---: |
| Correct references | 7/7 | 7/7 | equal |
| Total tokens | 29,365 | 18,655 | Rubydex -36.5% |
| Input tokens | 28,031 | 17,674 | Rubydex -36.9% |
| Output tokens | 1,334 | 981 | Rubydex -26.5% |
| Runner wall-clock | 57 s | 96 s | contaminated |

The token comparison is useful. The latency comparison is not: Run B included human approval delays and unrelated MCP startup/authentication noise.

## Second attempt

The runner was changed to `approval_policy = "never"` plus `sandbox_mode = "read-only"` to eliminate human approval pauses.

### Run A - valid

The second text-only run again returned all seven references and correctly separated `Admin::Reservation` and all 40 noise-domain constants.

```text
Elapsed runner time: 86 s
Codex reported work time: 63 s
Total tokens: 25,686
Input tokens: 23,876
Output tokens: 1,810
Cached input: 83,456
Correct references: 7/7
Edits: none
```

This reinforces that the text condition itself has substantial stochastic variance: 57 s / 29,365 tokens on the first run versus 86 s / 25,686 tokens on the second.

### Run B - invalid

The semantic run stopped before discovery. Both Rubydex calls failed with:

```text
MCP tool call requires approval, but approval policy is never
```

The resulting `30 s / 9,609 tokens` are **not benchmark measurements** and must not be compared with A. They measure a configuration failure, not semantic navigation.

## Runner correction after second attempt

Codex supports MCP-specific tool approval policy. Discovery runs now use:

```text
global approval_policy = never
global sandbox_mode = read-only
Rubydex default_tools_approval_mode = approve
```

This preserves a non-interactive, read-only benchmark while explicitly allowing the Rubydex MCP calls.

The runner also disables the known unrelated `cloudflare-api` and `reui` MCP servers for the benchmark invocation so their authentication/startup state does not contaminate the run.

## Current signal

At medium scale:

- correctness: text and Rubydex both achieved 7/7 in valid runs
- token/context efficiency: the first valid Rubydex run used about 36.5% fewer total tokens than the first text run
- repeatability: text navigation already shows meaningful run-to-run variance
- latency: still inconclusive until a clean Rubydex repeat completes without approval interaction

Next step: run **only B/medium once** with the corrected MCP-specific auto-approval. If it succeeds cleanly, compare it against both valid A runs before deciding whether another paired medium run is worth the usage cost.