# Lab 07 — task-shape boundary

## Goal

Find where Rubydex changes role for a coding agent on the same real Rails codebase and the same target constant.

Labs 04–05 showed two different effects:

- narrow semantic discovery can reduce search/context;
- broad impact mapping can improve structural correctness without reducing input tokens.

Lab 07 holds repository, revision, target, model, and runner isolation constant while increasing only the breadth of the requested task.

## Fixed subject

- Repository: `discourse/discourse`
- Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Target: `Categories::Types::Base`

## Task ladder

1. `declaration` — locate the target declaration.
2. `descendants` — enumerate named subclasses.
3. `references` — enumerate direct production references.
4. `neighborhood` — declaration + descendants + production references.
5. `impact` — full structural impact map: declaration, descendants, production references, plugin extensions, direct-reference specs, and a bounded read-first set.

The ladder intentionally reuses one frozen ground truth. This makes the experiment about **task shape**, not about differences between repositories or targets.

## Conditions

```text
A = ordinary repository navigation; no Rubydex
B = Rubydex semantic-first navigation; narrowed source reads are allowed for verification/classification
```

Both conditions use the same model, reasoning effort, prompt body, fresh GitHub-hosted VM, pinned Discourse revision, and read-only Codex permission profile.

## Output contract

Every task returns JSON only. The required keys depend on the scenario and use canonical `path:line` or `Name | path:line` strings. Deterministic set scoring avoids judging prose quality.

## What we measure

Per scenario and condition:

- exact structural correctness;
- wall-clock agent time;
- input / cached / uncached input tokens;
- output / reasoning tokens;
- estimated API cost using the harness price table.

For `impact`, read-first rubric coverage is reported separately from structural exactness.

## Hypothesis

Rubydex should have little economic advantage on trivial lookup, become a token/context saver on concentrated semantic discovery, and become primarily a correctness/reliability tool as the task expands into multi-part impact mapping that requires source verification and classification.

The interesting output is the **crossover curve**, not a single winner.
