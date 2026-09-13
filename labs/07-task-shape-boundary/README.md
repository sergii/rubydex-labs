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

## Observed repeated result

The 3×A + 3×B run per scenario found the crossover immediately after trivial declaration lookup:

| Scenario | Exact A | Exact B | B vs A time | B vs A total tokens | B vs A cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| declaration | 3/3 | 3/3 | +63.4% | +141.7% | +43.5% |
| descendants | 1/3 | 3/3 | -18.0% | -37.3% | -36.2% |
| references | 3/3 | 3/3 | -27.0% | -50.9% | -42.2% |
| neighborhood | 2/3 | 3/3 | -16.8% | -28.4% | -25.2% |
| impact | 1/3 | 3/3 | +3.3% | -33.7% | -22.7% |

Working interpretation: ordinary navigation wins for a single declaration lookup; once the task asks for a semantic relationship set, Rubydex amortizes its overhead and becomes a context/cost saver, with an additional correctness benefit on descendants, neighborhood, and impact tasks. Broad impact mapping keeps the context advantage but wall time flattens because source verification and synthesis dominate.

Full result: [`benchmarks/results/2026-09-13-lab-07-task-shape-boundary.md`](../../benchmarks/results/2026-09-13-lab-07-task-shape-boundary.md).
