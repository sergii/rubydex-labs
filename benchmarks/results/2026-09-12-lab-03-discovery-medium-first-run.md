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

## Third launch attempt - invalid before Codex startup

An attempted fix tried to disable unrelated global MCP servers through runtime overrides. Codex still parsed the user's global configuration before applying those overrides and exited immediately because the existing `cloudflare-api` entry used an invalid transport for this Codex version:

```text
Error loading config.toml: invalid transport
in `mcp_servers.cloudflare-api`
```

This attempt consumed effectively no benchmark time and produced no benchmark result.

## Final runner isolation

Discovery runners now use a dedicated temporary `CODEX_HOME` for each run instead of merging with the user's global Codex configuration.

The benchmark home contains only:

```text
model = gpt-6-astra
model_reasoning_effort = xhigh
approval_policy = never
sandbox_mode = read-only
```

For semantic runs it additionally contains only the project-local Rubydex MCP server with:

```text
enabled = true
required = true
default_tools_approval_mode = approve
```

If the user's normal Codex login is stored in `~/.codex/auth.json`, the benchmark home symlinks that auth file but does not import `~/.codex/config.toml`, unrelated MCP servers, hooks, or other user configuration.

The model and reasoning level can be overridden explicitly with:

```text
RUBYDEX_LABS_MODEL
RUBYDEX_LABS_REASONING
```

This makes A and B reproducible and prevents unrelated MCP configuration from affecting startup or timing.

## Current signal

At medium scale:

- correctness: text and Rubydex both achieved 7/7 in valid runs
- token/context efficiency: the first valid Rubydex run used about 36.5% fewer total tokens than the first text run
- repeatability: text navigation already shows meaningful run-to-run variance
- latency: still inconclusive until a clean Rubydex repeat completes under the isolated Codex configuration

Next step: run **only B/medium once** with the isolated benchmark Codex home. If it succeeds cleanly, compare it against both valid A runs before deciding whether to move to `large`.