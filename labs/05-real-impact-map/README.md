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

The final benchmark task will ask for:

1. declaration location;
2. descendants / subclasses of `Categories::Types::Base`;
3. direct production constant users;
4. plugin extensions / subclasses;
5. relevant spec files that directly exercise or reference the target;
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

The scout is not a benchmark measurement. It establishes a frozen structural ground truth using Rubydex and source spot-checks.

Run:

```bash
bin/scout-real-discourse impact
```

Check later with:

```bash
bin/real-discourse-status impact-scout
```

The scout should report exact descendants, exact constant references grouped by core/plugin/spec, and a candidate read-first set. After review, the structural facts will be frozen before any A/B run.

## Phase 2 - benchmark

After the scout result is frozen, Lab 05 will use the same counterbalanced protocol as Lab 04:

```text
A = normal repository navigation, no Rubydex
B = Rubydex semantic-first navigation
```

Both conditions will use the same pinned repository revision, model, reasoning level, read-only headless runner, and task wording apart from the semantic-first instruction in B.

Run order will be counterbalanced with `AB` and `BA` pairs so filesystem/order effects are visible.

## Scoring plan

Structural facts will be scored automatically where an exact set is meaningful:

- descendant recall / false positives;
- direct production-reference recall / false positives;
- plugin-extension recall / false positives;
- relevant direct-reference spec-file recall / false positives.

The read-first set is intentionally a prioritization task, so it will not be treated as a single exact ground-truth set. It will instead be evaluated for coverage of frozen must-read categories, size, and justification quality.
