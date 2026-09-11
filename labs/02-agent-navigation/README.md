# Lab 02 - Agent navigation

## Question

Does semantic code navigation reduce exploration cost and mistakes for a coding agent compared with text search alone?

The lab now has three conditions so we can separate tool availability from tool-use strategy.

## Fixture

The Rails fixture deliberately contains:

- `Inventory::Reservation`, the constant that must be renamed
- `Admin::Reservation`, an unrelated constant with the same unqualified name
- references written as both `Inventory::Reservation` and plain `Reservation`
- inheritance through an unqualified `Reservation`
- strings containing the same words but no Ruby constant reference

This makes text matching different from semantic reference resolution.

## One-command runs

Use fresh Codex sessions for each condition:

```bash
bin/run-lab-a
bin/run-lab-b
bin/run-lab-c
```

Or use the generic launcher:

```bash
bin/run-lab A
bin/run-lab B
bin/run-lab C
```

The runners recreate isolated `/tmp` workspaces, install/check dependencies before timing, create a Git baseline, launch Codex with the correct project-local MCP configuration, and save the final patch.

## Run A - text navigation only

`bin/run-lab-a`

The control fixture removes Rubydex from the project and disables the Rubydex MCP server.

The agent receives only [`task.md`](task.md) and may use ordinary repository navigation such as file listing, `rg`, `grep`, and file reads.

This condition asks:

> How well can the coding agent solve the task with normal text/file navigation?

## Run B - Rubydex available

`bin/run-lab-b`

The fixture includes Rubydex and exposes the project-local MCP server:

```bash
bundle exec rdx mcp
```

The agent receives the exact same [`task.md`](task.md) as Run A. It gets no instruction about when or how to use Rubydex.

This condition asks:

> Does a coding agent naturally use an available semantic code-intelligence tool efficiently?

The first observed A/B run showed that tool availability alone was not enough: the agent performed substantial text exploration before calling Rubydex, so semantic lookup became additional work rather than replacing exploration.

## Run C - semantic-first Rubydex

`bin/run-lab-c`

The fixture and MCP setup are the same as Run B, but the agent receives [`task-semantic-first.md`](task-semantic-first.md).

Before broad repository text search or reading candidate source files, it must:

1. resolve `Inventory::Reservation`
2. retrieve all resolved constant references
3. resolve `Admin::Reservation` and its references
4. choose files to inspect from those semantic results

Text search is allowed afterward for validation and non-semantic checks.

This condition asks:

> If semantic navigation is used as the primary discovery mechanism rather than an optional extra tool, does it reduce exploration, tokens, or wall-clock time?

Run C intentionally changes the navigation strategy. It is therefore not a prompt-identical A/B comparison. It is a strategy experiment designed to explain the A/B result.

## Record

For each run capture:

- final patch correctness
- number of real references found
- false positives investigated
- files read before the edit
- broad text-search calls before the edit
- Rubydex MCP calls before the edit
- total search/tool calls
- tokens used, when Codex reports them
- Codex reported work time
- runner wall-clock duration
- time to first correct model of the dependency set

Copy [`../../benchmarks/run-template.md`](../../benchmarks/run-template.md) for each result.

## Fairness rules

For A vs B:

- same source commit
- same model and thinking level
- exact same task wording
- fresh conversation/session
- separate fixture directories
- no transcript sharing
- no manual hints after the run starts

For C, keep the same source, model, and session isolation, but explicitly record that the navigation strategy is prescribed.

Dependency installation time is outside the timed agent run.

## Important observation about MCP freshness

In the first Run B, Rubydex correctly returned the original declaration and all seven resolved references before editing. After files were changed, a later MCP query still returned the old graph state and did not find the new declaration.

For now, treat Rubydex MCP as a discovery index whose post-edit freshness must be verified rather than assumed. Final correctness should be checked with source/runtime tools such as Zeitwerk, Rails tests, or targeted text validation.

A future lab should test incremental MCP re-indexing explicitly.

## Next scaling experiment

Do not change fixture size until Run C is complete. Otherwise codebase complexity and navigation strategy change at the same time.

After A/B/C are measured on the same fixture, create a larger deterministic fixture with many namespace collisions, unrelated `Reservation` declarations, inherited references, reopened declarations, and textual noise. Then rerun the three conditions to find the point where semantic navigation starts paying for itself.
