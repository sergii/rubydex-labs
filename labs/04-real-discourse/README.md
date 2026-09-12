# Lab 04 - Real Discourse codebase

## Goal

Validate the Lab 03 result on a real, actively maintained production Rails monolith instead of a synthetic fixture.

Repository: `discourse/discourse`

Pinned revision:

```text
c89b1a0506a3ec0a249b7f23ac86763b358dc177
```

The benchmark never follows `main`; every run uses this exact revision.

## Why Discourse

Discourse is a large real Rails monolith with core application code, plugins, specs, jobs, services, serializers, migrations, scripts, and many repeated short constant names across different namespaces.

This makes it a better test of semantic navigation than adding more generated noise to Lab 03.

## Frozen target

Target declaration:

```text
Categories::Types::Base
```

The target was selected before any timed A/B run.

Reasons:

- it is production code in `app/services/categories/types/base.rb`
- core code contains an unqualified reference: `class Discussion < Base`
- plugins and specs contain qualified references to the same declaration
- the repository contains many unrelated declarations named `Base`
- comments and prose also mention the fully qualified name

That combination creates real constant-resolution ambiguity without manufacturing decoy files.

## Phase 1 - scout

The scout is not a benchmark measurement. It uses Rubydex to establish the semantic reference set and codebase statistics for the pinned revision.

The completed scout indexed:

```text
15,130 files
137,534 declarations
145,449 definitions
453,208 constant references
1,559,344 method references
```

It resolved the target to `app/services/categories/types/base.rb:5`, found 21 resolved constant references, and found 2,574 visible exact-name declaration matches for `Base`.

The 21-reference set is frozen in `ground-truth.txt`; the full scout summary is in `scout-result.md`.

## Phase 2 - benchmark

The same discovery task runs under two conditions:

- A: normal text/file navigation, no Rubydex MCP
- B: Rubydex semantic-first navigation

Both use the same model, reasoning level, pinned Discourse revision, read-only headless Codex runner, and exact task target. The frozen ground truth is used only by the post-run scoring harness and is not copied into the benchmark workspace or prompt.

Run an A -> B pair:

```bash
bin/run-real-discourse-pair AB
```

Check it later with:

```bash
bin/real-discourse-pair-status AB
```

Then counterbalance the order:

```bash
bin/run-real-discourse-pair BA
bin/real-discourse-pair-status BA
```

Each condition resets and cleans the pinned checkout before starting. This removes untracked index/cache artifacts from earlier conditions. Running both `AB` and `BA` also helps expose filesystem-cache or order effects.

The task is discovery only: no edits, Rails boot, tests, or dependency installation inside the timed model run.

## Metrics

The pair harness records:

- exact-reference recall against the 21 frozen references
- false positives and precision
- exact-answer status
- elapsed model-session time
- total/input/cached/uncached/output/reasoning tokens
- both final answers for manual inspection

Rubydex MCP startup/indexing remains inside B's measured session time; it is not pre-subtracted.

## Important caveat

The scout uses Rubydex to establish semantic ground truth, so the final benchmark report must distinguish two questions:

1. Does Rubydex let the agent reach Rubydex's resolved-reference set more cheaply?
2. Are those resolved references actually correct Ruby semantics?

The target and representative references were independently source-spot-checked before the benchmark, including the unqualified `Categories::Types::Discussion < Base` reference and fully-qualified plugin subclasses. A broad publication claim would still benefit from independent verification of the complete 21-reference set.
