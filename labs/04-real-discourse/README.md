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

Run:

```bash
bin/scout-real-discourse
```

Then inspect:

```bash
bin/real-discourse-status scout
```

The scout result is used to freeze the ground truth before any timed A/B comparison.

## Phase 2 - benchmark

After the scout output is reviewed and the reference set is frozen in this lab, run the same discovery task under two conditions:

- A: normal text/file navigation, no Rubydex MCP
- B: Rubydex semantic-first navigation

Both conditions will use the same model, reasoning level, pinned Discourse revision, and read-only headless Codex runner.

The task is discovery only: no edits, Rails boot, tests, or dependency installation inside the timed model run.

## Metrics

Record:

- exact-reference recall
- false positives
- elapsed model-session time
- total/input/cached/uncached/output/reasoning tokens
- search/tool behavior
- number of source files inspected when available

## Important caveat

The scout uses Rubydex to establish semantic ground truth, so the final benchmark report must distinguish two questions:

1. Does Rubydex let the agent reach Rubydex's resolved-reference set more cheaply?
2. Are those resolved references actually correct Ruby semantics?

Before publishing a broad claim, the frozen ground truth should be independently spot-checked against source structure and, where practical, another implementation or runtime behavior.
