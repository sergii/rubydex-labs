# Lab 02 result - Agent navigation A/B/C

Date: 2026-09-12

## Question

Does Rubydex semantic navigation reduce coding-agent exploration cost for a Rails rename task?

All three runs used the same fixture and produced the same correct patch: rename `Inventory::Reservation` to `Inventory::Allocation`, update all seven real references, preserve `Admin::Reservation`, strings, labels, and table names.

## Conditions

- **A - text only:** Rubydex unavailable. Codex used repository listing, text search, source reads, and runtime verification.
- **B - Rubydex available:** Rubydex MCP was available, but Codex chose its own navigation strategy.
- **C - semantic first:** Codex was explicitly required to resolve the declaration and references with Rubydex before broad text search or candidate-file reads.

All runs used Codex `gpt-6-astra` at `xhigh` according to the recorded session headers.

## Results

| Metric | A - text only | B - Rubydex available | C - semantic first |
| --- | ---: | ---: | ---: |
| Correct final patch | yes | yes | yes |
| Real references found | 7/7 | 7/7 | 7/7 |
| Runner wall-clock | **98 s** | 119 s | 177 s |
| Codex reported work time | **84 s** | 112 s | 163 s |
| Total tokens | **25,596** | 28,859 | 29,711 |
| Rubydex semantic calls before edit | 0 | 3 | 4 |

Relative to A:

- B was about **21% slower** and used about **13% more tokens**.
- C was about **81% slower** and used about **16% more tokens**.

Relative to B, C was about **49% slower** and used about **3% more tokens**.

## What C proved

The semantic discovery itself worked exactly as intended.

Before reading candidate source files, Rubydex returned:

- the declaration of `Inventory::Reservation`
- exactly seven resolved constant references
- the separate declaration of `Admin::Reservation`
- exactly one resolved reference to the admin constant

At that point the agent already had the complete semantic dependency set needed for the rename.

This is strong evidence that Rubydex can answer the navigation question deterministically and with high precision.

## Why C was still slower

After semantic discovery, Codex continued with much of the work that the semantic step was intended to replace or narrow:

- repository/file listing
- broad text search for `Reservation|reservation|Allocation|allocation`
- reading project configuration
- reading all candidate files
- Ruby syntax checks
- Zeitwerk validation
- another broad text search
- a Rails runner with 17 runtime assertions
- repeated status/diff checks and cleanup

The semantic result reduced uncertainty, but it did not reduce the model's verification behavior. On this tiny fixture, verification dominates navigation cost.

## Interpretation

The first three runs answer three different questions:

1. **Can a strong coding agent solve this tiny Rails task without Rubydex?** Yes.
2. **Will the agent automatically exploit Rubydex efficiently just because MCP is available?** Not in this run.
3. **Does forcing semantic-first navigation make the whole task faster on this tiny fixture?** No.

The important positive result is narrower: Rubydex produced the exact declaration/reference set immediately, while text navigation had to reconstruct that set from source and lexical search.

The current end-to-end benchmark is too small and too dominated by validation to reveal whether semantic navigation pays off as repository ambiguity grows.

## Next experiment

Separate **discovery** from **editing/verification** and scale repository ambiguity.

The next benchmark should ask only:

> Identify every Ruby reference that resolves to `Inventory::Reservation`, distinguish unrelated same-named constants, and return the exact affected files and locations. Do not edit files.

Run that task on deterministic fixture sizes such as small, medium, and large. Add many unrelated `Reservation` declarations, unqualified references, inheritance paths, and textual strings.

Measure:

- correctness / recall
- false positives
- tool calls
- files read
- tokens
- wall-clock time

This isolates the capability Rubydex is designed to improve instead of measuring Rails verification behavior.