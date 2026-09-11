# Lab 02 result - Agent navigation, first run

Date: 2026-09-12

## Scenario

Both runs used the same task and equivalent isolated Rails fixtures:

> Rename `Inventory::Reservation` to `Inventory::Allocation`, update every real Ruby reference, preserve the unrelated `Admin::Reservation`, and leave prose/historical strings unchanged.

Run A exposed ordinary filesystem/text navigation only. Run B additionally exposed the Rubydex MCP server.

## Environment

- OpenAI Codex CLI v0.154.0
- Model reported by both sessions: `gpt-6-astra xhigh`
- Same task wording
- Fresh isolated fixture for each run
- Same local machine
- Dependencies installed before the timed agent session

Note: the user intended to use the same Codex "Standard" configuration for both runs. The CLI banner reported `gpt-6-astra xhigh` in both sessions, so the pair is internally comparable, but this should be clarified before future benchmark series.

## Run A - text navigation only

Observed navigation pattern:

1. Enumerated Ruby/project files.
2. Used broad `rg` search for `Reservation|Allocation`.
3. Inspected the candidate files.
4. Correctly inferred one declaration and seven real references.
5. Edited five source locations plus the defining file rename.
6. Ran Rails/Zeitwerk and runtime smoke verification.

Result:

- Correct declaration identified: yes
- Correct real references identified before edit: 7/7
- `Admin::Reservation` preserved: yes
- Prose/historical strings preserved: yes
- Final patch correct: yes
- Codex reported work time: 1m 24s
- Runner elapsed session time: 98s
- Token usage: 25,596 total
  - input: 23,632
  - output: 1,964
  - reasoning: 313
  - cached input reported separately: 208,256

## Run B - Rubydex MCP available

Observed navigation pattern:

1. Enumerated Ruby/project files.
2. Still performed broad `rg` search before using Rubydex.
3. Read a broad set of candidate files.
4. Called `rubydex.get_declaration("Inventory::Reservation")`.
5. Called `rubydex.find_constant_references("Inventory::Reservation")`, which returned exactly seven resolved references.
6. Separately queried `Admin::Reservation`, which returned one unrelated reference.
7. Edited the same five source locations plus the defining file rename.
8. Ran Rails/Zeitwerk and runtime smoke verification.

Result:

- Correct declaration identified: yes
- Correct real references identified before edit: 7/7
- Rubydex resolved references: exactly 7
- `Admin::Reservation` semantically distinguished: yes
- `Admin::Reservation` preserved: yes
- Prose/historical strings preserved: yes
- Final patch correct: yes
- Codex reported work time: 1m 52s
- Runner elapsed session time: 119s
- Token usage: 28,859 total
  - input: 26,299
  - output: 2,560
  - reasoning: 363
  - cached input reported separately: 279,680

## Comparison

| Metric | Run A - text | Run B - Rubydex MCP |
| --- | ---: | ---: |
| Final patch correct | yes | yes |
| Real references identified | 7/7 | 7/7 |
| Semantic proof of exact references | inferred from source | explicit Rubydex result |
| Runner elapsed time | 98 s | 119 s |
| Codex reported work time | 84 s | 112 s |
| Total tokens | 25,596 | 28,859 |
| Input tokens | 23,632 | 26,299 |
| Output tokens | 1,964 | 2,560 |
| Reasoning tokens | 313 | 363 |

On this first small fixture, simply making Rubydex available did **not** reduce elapsed time or token usage. Run B was about 21% slower by runner elapsed time (`119 / 98`) and used about 13% more total tokens (`28,859 / 25,596`). Both runs were correct.

## Why the treatment did not win

The main reason is visible in the agent trace: Run B did not replace broad exploration with semantic navigation. It first performed the same file enumeration, broad text search, and source inspection as Run A, and only then used Rubydex. In this run, Rubydex was additive work rather than a substitute for text exploration.

This answers one useful question:

> Does merely exposing Rubydex MCP to a capable coding agent automatically improve a small rename task?

For this run, no.

It does **not** yet answer a different question:

> Can a semantic-first workflow using Rubydex reduce exploration on larger or more ambiguous Ruby codebases?

That requires a separate treatment where the workflow intentionally starts with semantic queries, or a larger fixture where text exploration becomes materially more expensive.

## Important MCP observation after editing

After the source edits, Run B called Rubydex again. The MCP server still returned the old seven `Inventory::Reservation` references and could not find `Inventory::Allocation`.

That suggests the MCP graph in this invocation was a startup snapshot rather than automatically updated after direct filesystem edits, or that change propagation was not wired into this Codex/MCP setup. The final Rails checks passed, so the source edits themselves were correct.

This behavior matters for agent workflows. Rubydex was highly useful for **pre-edit semantic discovery**, but the same server instance was not reliable as a post-edit verification source in this run. Future labs should verify whether the MCP server supports file watching/reindexing or needs a restart/reindex after edits.

## Interpretation

The first Lab 02 run is valuable specifically because it did not confirm the expected performance advantage.

What Rubydex clearly added:

- deterministic identification of the target declaration
- exact resolved reference count
- explicit separation of `Inventory::Reservation` and `Admin::Reservation`
- semantic confirmation of the unqualified `Reservation` superclass/reference sites

What it did not add in this run:

- fewer initial searches
- fewer files inspected
- lower token usage
- lower wall-clock duration

The fixture is small enough that a strong coding model can reconstruct Ruby constant resolution cheaply from a handful of files.

## Recommended next experiments

1. Repeat A/B several times to estimate stochastic variance.
2. Add a semantic-first Run C where the agent is explicitly instructed to query Rubydex before broad text search. This tests the tool capability separately from the agent's default navigation policy.
3. Scale the fixture to dozens or hundreds of relevant-looking `Reservation` occurrences, nested namespaces, inherited references, reopened declarations, and misleading text matches.
4. Test a task where semantic structure is harder to infer textually, such as transitive ancestors, architecture boundaries, or impact analysis across many namespaces.
5. Investigate MCP graph freshness after edits and document the expected reindex/restart behavior.
