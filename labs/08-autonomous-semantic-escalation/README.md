# Lab 08 — autonomous semantic escalation

## Goal

Measure whether a coding agent autonomously chooses Rubydex when semantic navigation is economically useful on a real Rails monolith, and whether a minimal tool-selection policy improves that decision without forcing semantic-first behavior.

This lab follows two prior observations on the same pinned Discourse target:

- forced semantic-first navigation materially improved correctness and reduced context cost for relationship-set and impact-map tasks;
- on a tiny synthetic fixture, merely making Rubydex available produced zero Rubydex calls because scanning the whole fixture was cheaper.

Lab 08 holds repository, revision, target, task, model, reasoning effort, output contract, and shared analysis guidance constant while changing only semantic-tool availability and the decision policy.

## Fixed subject

- Repository: `discourse/discourse`
- Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Target: `Categories::Types::Base`
- Task: the Lab 07 `impact` scenario
- Ground truth: reused unchanged from `labs/07-task-shape-boundary/ground-truth.json`

## Conditions

```text
D = ordinary source navigation only

E = identical prompt + Rubydex MCP available but optional
    the prompt does not mention Rubydex or require semantic tooling

F = Rubydex MCP available but optional + one minimal decision rule:
    use deterministic semantic evidence first when the task depends on
    repository-wide semantic relationship sets and broad source traversal
    would be expensive; otherwise use ordinary navigation
```

E tests natural tool discovery/selection. F tests whether a small policy can create rational escalation without returning to `semantic-first everywhere`.

## Shared guidance

All three conditions receive the same grounding rules:

- distinguish resolved references from lexical matches;
- separate production, plugin, and spec evidence;
- do not infer relationships from naming alone;
- return the same strict JSON output contract;
- do not edit source, boot Rails, or run tests.

## What we measure

Correctness:

- exact structural impact-map correctness;
- per-set precision/recall for descendants, production references, plugin extensions, and direct-reference specs;
- read-first rubric coverage.

Navigation economics:

- Rubydex/MCP tool-call count;
- semantic tool names observed in Codex logs;
- shell command count;
- search-command count (`rg`, `grep`, `find`);
- approximate unique Ruby source files whose contents were printed/read;
- elapsed time;
- total, cached, and uncached input tokens;
- output/reasoning tokens;
- estimated API cost using the repository benchmark price table.

The source-file count is intentionally an operational approximation derived from command logs, not a claim about every byte visible to the model.

## Hypotheses

1. D should resemble the ordinary-navigation side of Lab 07 and pay substantial search/context cost.
2. E may or may not call Rubydex; the important measurement is the selection behavior itself.
3. F should call semantic tooling when repository-wide relationships dominate the task, then use source reads only for verification/classification.
4. If F approaches forced semantic-first correctness/context efficiency with fewer unnecessary semantic calls, it supports an escalation architecture rather than a universal semantic-first rule.

## Product question

The product-level question is not simply whether Rubydex is useful. It is:

> Can an agent learn when deterministic semantic evidence is worth its startup/query cost, and can that decision be encoded as a small reusable policy?
