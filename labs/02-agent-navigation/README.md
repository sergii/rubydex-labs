# Lab 02 - Agent navigation

## Question

Does semantic code navigation reduce exploration cost and mistakes for a coding agent compared with text search alone?

## Task

Use the exact prompt in [`task.md`](task.md) for both runs.

The codebase deliberately contains:

- `Inventory::Reservation`, the constant that must be renamed
- `Admin::Reservation`, an unrelated constant with the same unqualified name
- references written as both `Inventory::Reservation` and plain `Reservation`
- inheritance through an unqualified `Reservation`
- strings and Markdown containing the same words but no Ruby constant reference

This makes text matching different from semantic reference resolution.

## Run A - text navigation only

Start from a clean worktree. Do not configure the Rubydex MCP server and do not use `rdx query`.

The agent may use normal repository tools such as file listing, `rg`, `grep`, and file reads.

Example setup:

```bash
git worktree add ../rubydex-labs-control HEAD
cd ../rubydex-labs-control
bundle install
```

Give the agent only the task prompt and normal repository access.

## Run B - Rubydex semantic navigation

Start from the exact same commit in a second clean worktree.

```bash
git worktree add ../rubydex-labs-semantic HEAD
cd ../rubydex-labs-semantic
bundle install
```

Configure the coding client to expose this project-local MCP command:

```bash
bundle exec rdx mcp
```

The Rubydex MCP server exposes semantic operations such as declaration lookup, descendants, and resolved constant references.

Give the agent the exact same task prompt. Do not show it the control transcript or patch.

## Suggested treatment strategy

The treatment agent should begin with semantic questions before broad text search:

```text
Find the declaration Inventory::Reservation.
Find resolved references to that declaration.
Inspect declarations/files containing those references.
Read only the source needed to make the rename.
```

It may still use text search afterward. The experiment is not "MCP only". It is whether semantic navigation changes the amount and quality of exploration.

## Record

For each run capture:

- final patch correctness
- number of real references found
- false positives investigated
- files read
- search/tool calls
- tokens used, when the client reports them
- wall-clock duration
- time to first correct model of the dependency set

Copy [`../../benchmarks/run-template.md`](../../benchmarks/run-template.md) for each result.

## Fairness rules

- Same starting commit.
- Same model and thinking level.
- Same task wording.
- Fresh conversation/session for each run.
- No transcript sharing between runs.
- No manual hints after the run starts.
- Do not count dependency installation time as agent navigation time.
- Run each condition multiple times because agent behavior is stochastic.

## Expected pattern

A tiny task may show little difference. The value of semantic navigation should become clearer as we add more namespaces, inherited references, reopened declarations, and textual noise.

That scaling experiment is intentional. The lab should evolve from "does this work?" to "at what codebase complexity does it start paying for itself?"
