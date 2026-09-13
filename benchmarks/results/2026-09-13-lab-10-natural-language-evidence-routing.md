# Lab 10 — natural-language evidence routing

Recorded: 2026-09-13

- Classifier model: `gpt-5.6-luna` (`low` reasoning)
- Downstream model: `gpt-5.6-luna` (`medium` reasoning)
- Repository: `discourse/discourse`
- Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Final workflow run: `34767530736`

## Result

The natural-language classifier reproduced the hidden oracle route on every completed classification in the frozen corpus.

| Metric | H — natural-language classifier | O — oracle |
| --- | ---: | ---: |
| Classification correct | **36/36** | 36/36 |
| Route correct | **36/36** | 36/36 |
| Executed downstream tasks | 24 | 24 |
| Downstream exact | **23/24** | **24/24** |
| Observed backend route | **24/24** | **24/24** |

Classifier accuracy by evidence class:

| Expected class | Correct | Median sec | Median tokens | Median cost |
| --- | ---: | ---: | ---: | ---: |
| `SOURCE_LOCAL` | 9/9 | 1.52 | 496 | $0.0001 |
| `SEMANTIC_RELATIONSHIP_SET` | 15/15 | 1.42 | 509 | $0.0002 |
| `RUNTIME_BEHAVIOR` | 6/6 | 1.41 | 516 | $0.0002 |
| `ARCHITECTURE_KNOWLEDGE` | 6/6 | 1.74 | 511 | $0.0002 |

Condition medians:

| Cond | Class correct | Route correct | Downstream exact | Classifier tokens | Classifier cost | Agent tokens | Agent cost | Combined cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| H | 36/36 | 36/36 | 23/24 | 508 | $0.0002 | 57,588 | $0.0053 | $0.0055 |
| O | 36/36 | 36/36 | 24/24 | 0 | n/a | 67,728 | $0.0053 | $0.0053 |

## The single downstream miss

The only non-exact H sample was `semantic-02-H-r3`, a request for every direct production reference to `Categories::Types::Base`.

Routing was correct. Rubydex was invoked and returned the complete evidence. In particular:

- `get_descendants` included `DiscourseSolved::Categories::Types::Support`;
- `find_constant_references` included `plugins/discourse-solved/app/services/discourse_solved/categories/types/support.rb:6`;
- the final model answer nevertheless emitted four production references instead of five and omitted that item.

So the failure was not classifier error, router error, or missing semantic evidence. The model dropped an item while transforming a complete machine result into prose/JSON.

This establishes an important boundary:

> Models may interpret evidence. Models should not reconstruct authoritative complete sets when a deterministic backend can preserve them.

For `all`, `every`, or otherwise completeness-sensitive queries, the backend/filter layer should produce an explicit `EvidenceSet` with machine-owned membership and count. The model may explain that set, but should not manually recreate it.

## Interpretation

Lab 10 supports four conclusions.

1. **Evidence class is a useful product abstraction.** The frozen request corpus cleanly mapped ordinary engineering requests into source-local, semantic-relationship, runtime, or architecture-knowledge evidence classes.
2. **Routing can be separated from the main reasoning agent.** A low-reasoning classifier recovered the oracle route at negligible cost relative to downstream analysis.
3. **Rubydex is an evidence backend, not the architecture itself.** It is appropriate for resolved repository-wide semantic relationship sets; source, runtime, and architecture questions require different evidence paths.
4. **Completeness must be machine-owned.** The one downstream miss happened after the correct semantic result had already been obtained.

The practical architecture is therefore moving from implicit tool choice toward:

```text
engineering request
       |
       v
 evidence classifier / planner
       |
       v
 correct evidence backend(s)
       |
       v
 machine-preserved evidence
       |
       v
 model reasoning / explanation
```

## Limitations

This is not evidence that arbitrary production requests will be classified with 100% accuracy.

The corpus contains 12 unique requests repeated three times, and their evidence requirements are intentionally well separated. The classifier therefore demonstrated that this four-way evidence taxonomy is learnable on the frozen benchmark, not that routing is universally solved.

`RUNTIME_BEHAVIOR` and `ARCHITECTURE_KNOWLEDGE` were classification-only in Lab 10 because those backends are not wired into this repository. Source and semantic routes were executed end to end.

The current classifier chooses exactly one evidence class. Real engineering questions often require several kinds of evidence. The next architectural abstraction should therefore be an `EvidencePlan`, not merely a larger single-label classifier.

## Frozen takeaway

The key question is no longer "should the agent use Rubydex?"

It is:

> What is the cheapest reliable evidence path for this engineering question, and which deterministic facts must remain machine-owned before model reasoning begins?
