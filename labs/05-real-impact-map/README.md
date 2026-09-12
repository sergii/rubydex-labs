# Lab 05 - Real Discourse impact map

## Goal

Test a more realistic pre-change engineering task on the same pinned production Discourse codebase used in Lab 04.

Repository: `discourse/discourse`

Pinned revision:

```text
c89b1a0506a3ec0a249b7f23ac86763b358dc177
```

Target declaration:

```text
Categories::Types::Base
```

Instead of asking only for exact references, the agent must build a compact impact map before a hypothetical change.

## Required impact map

The benchmark asks for:

1. declaration location;
2. named descendants / subclasses of `Categories::Types::Base`;
3. direct production constant users;
4. plugin extensions / subclasses;
5. spec files containing direct references to the target;
6. a small read-first file set for an engineer preparing to change the target, with one short reason per file.

The agent must not edit code, boot Rails, run tests, or install dependencies.

## Why this is harder than Lab 04

Lab 04 measured one semantic primitive: exact constant-reference discovery.

Lab 05 combines several pieces of engineering judgment:

- inheritance topology;
- direct dependency discovery;
- core vs plugin boundaries;
- test impact;
- prioritizing a minimal reading set instead of returning every textual match.

This is closer to how a coding agent navigates a mature Rails application before making a change.

## Phase 1 - semantic scout

The scout is not a benchmark measurement. It establishes frozen structural ground truth using Rubydex and source spot-checks.

Run:

```bash
bin/scout-real-discourse impact
```

Check later with:

```bash
bin/real-discourse-status impact-scout
```

The completed scout returned 19 descendant entries and 21 resolved references. Because the benchmark prompt asks for named descendants, the scoring set excludes the target declaration itself and anonymous `Class.new(...)` descendants.

Frozen scoring data lives in:

```text
labs/05-real-impact-map/ground-truth.json
labs/05-real-impact-map/scout-result.md
```

## Phase 2 - benchmark

Conditions:

```text
A = normal repository navigation, no Rubydex
B = Rubydex semantic-first navigation
```

Both use the same pinned repository revision, model, reasoning level, read-only headless runner, and frozen task wording apart from B's semantic-first instruction.

Run A -> B:

```bash
bin/run-real-impact-pair AB
```

Check progress/result:

```bash
bin/real-impact-pair-status AB
```

After it completes, counterbalance the order:

```bash
bin/run-real-impact-pair BA
bin/real-impact-pair-status BA
```

Do not run AB and BA simultaneously because both conditions use the same pinned checkout and reset/clean it before each run.

## Frozen structural ground truth

The automatic scorer expects:

- declaration: 1 exact location
- named descendants: 5
- direct production references: 5
- plugin extensions: 3
- direct-reference spec files: 8

The read-first set is not scored as one exact file set. Instead, it is evaluated against five frozen coverage categories:

1. target implementation
2. core subclass
3. at least one plugin extension
4. direct base spec
5. at least one representative integration/direct-reference spec

The task allows at most 12 read-first files. The scorer also records whether every entry includes a non-empty reason.

## Metrics

The pair harness records:

- exact declaration correctness
- recall and false positives for each structural set
- whether all structural sets are exact
- read-first category coverage and set size
- elapsed model-session time
- total/input/cached/uncached/output/reasoning tokens
- both final answers for manual inspection

Rubydex MCP startup/indexing remains inside B's measured time.
