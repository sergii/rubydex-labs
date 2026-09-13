# Lab 07 — task-shape boundary on fresh GitHub runners

Date: 2026-09-13

## Setup

- Repository under analysis: `discourse/discourse`
- Pinned revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Target: `Categories::Types::Base`
- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Samples: 3 per condition per scenario
- Scenarios: `declaration`, `descendants`, `references`, `neighborhood`, `impact`
- Each sample ran on a separate fresh GitHub-hosted VM.
- A: ordinary repository navigation, no Rubydex MCP.
- B: Rubydex semantic-first navigation.
- Rubydex MCP startup/indexing remained inside the measured Codex session.
- All samples were read-only and used the official `openai/codex-action` with the API key supplied through GitHub Actions secrets.

Source benchmark workflow run: `34754925408`
Post-run report workflow run: `34755605759`

## Crossover table

| Scenario | Exact A | Exact B | A sec | B sec | B vs A time | A uncached | B uncached | B vs A uncached | A total | B total | B vs A total | A cost | B cost | B vs A cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| declaration | 3/3 | 3/3 | 4.0 | 6.5 | +63.4% | 11,047 | 13,506 | +22.3% | 20,940 | 50,612 | +141.7% | $0.0027 | $0.0039 | +43.5% |
| descendants | 1/3 | 3/3 | 21.1 | 17.3 | -18.0% | 26,849 | 16,706 | -37.8% | 118,112 | 74,039 | -37.3% | $0.0095 | $0.0060 | -36.2% |
| references | 3/3 | 3/3 | 16.5 | 12.1 | -27.0% | 23,061 | 15,073 | -34.6% | 109,835 | 53,907 | -50.9% | $0.0082 | $0.0047 | -42.2% |
| neighborhood | 2/3 | 3/3 | 25.7 | 21.4 | -16.8% | 24,714 | 18,371 | -25.7% | 110,596 | 79,172 | -28.4% | $0.0092 | $0.0069 | -25.2% |
| impact | 1/3 | 3/3 | 35.9 | 37.1 | +3.3% | 33,229 | 25,011 | -24.7% | 160,679 | 106,545 | -33.7% | $0.0132 | $0.0102 | -22.7% |

## Token decomposition

| Scenario | A input | B input | Δ input | A cached | B cached | Δ cached | A output | B output | Δ output | A reasoning | B reasoning | Δ reasoning |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| declaration | 20,702 | 50,260 | +142.8% | 9,655 | 36,754 | +280.7% | 238 | 352 | +47.9% | 87 | 122 | +40.2% |
| descendants | 116,186 | 73,128 | -37.1% | 89,337 | 56,231 | -37.1% | 1,605 | 1,368 | -14.8% | 761 | 562 | -26.1% |
| references | 108,277 | 53,113 | -50.9% | 85,216 | 38,040 | -55.4% | 1,558 | 794 | -49.0% | 572 | 310 | -45.8% |
| neighborhood | 108,404 | 77,593 | -28.4% | 83,690 | 58,292 | -30.3% | 1,926 | 1,660 | -13.8% | 1,027 | 722 | -29.7% |
| impact | 157,303 | 103,221 | -34.4% | 124,074 | 78,289 | -36.9% | 3,376 | 3,095 | -8.3% | 1,518 | 1,462 | -3.7% |

For the `impact` scenario, median read-first rubric coverage was 4/5 for A and 5/5 for B.

## Interpretation

This experiment exposes a clear task-shape crossover.

### 1. Trivial lookup: Rubydex is overhead

For `declaration`, both conditions were exact 3/3. Ordinary repository navigation finished in about 4.0 seconds, while Rubydex took 6.5 seconds and consumed substantially more context. A semantic index is not economically justified when the task is effectively “find this one declaration.”

### 2. Semantic set discovery: Rubydex starts paying for itself

The crossover appears as soon as the task asks for a relationship set instead of a single lookup.

For `descendants`, Rubydex improved exactness from 1/3 to 3/3 while reducing median time by 18%, total tokens by 37%, uncached input by 38%, and estimated cost by 36%.

For `references`, both conditions were exact 3/3, but Rubydex cut median total tokens by about 51%, uncached input by 35%, time by 27%, and estimated cost by 42%. This is the cleanest economic win in the ladder.

### 3. Small semantic neighborhood: accuracy and efficiency compound

For `neighborhood` — declaration plus descendants plus production references — Rubydex improved exactness from 2/3 to 3/3 and reduced median time by 17%, total tokens by 28%, and estimated cost by 25%.

This suggests that graph-shaped queries amortize the semantic-tool startup/indexing cost quickly once the agent needs more than one relationship.

### 4. Broad impact map: context savings remain, latency flattens

For `impact`, Rubydex was exact 3/3 versus 1/3 for ordinary navigation and improved read-first coverage from a median 4/5 to 5/5. It also used 34% fewer total tokens and 25% fewer uncached input tokens. Wall time, however, was effectively flat at +3.3% for B.

That shape is plausible: semantic discovery removes a large amount of repository search, but the agent still has to classify production/plugin/spec context and construct a useful read-first set. The semantic graph saves context, while source-level synthesis still costs time.

## Practical crossover model

A useful working model from this target is:

```text
single declaration lookup
    → normal text/navigation wins

one semantic relationship set
    → Rubydex begins to amortize its overhead

multiple related semantic sets
    → Rubydex tends to win on both correctness and context cost

broad impact/change planning
    → Rubydex remains a correctness/context advantage,
      while wall time becomes dominated by source verification and synthesis
```

The strongest observed sweet spot is exact semantic discovery (`references` / `descendants`), not trivial lookup and not necessarily broad reasoning latency.

## Important comparison with Lab 05

Lab 05 tested a similar broad impact-map task on the same target and also found a strong correctness effect: A was 0/3 exact and B was 3/3 exact. However, Lab 05 reported **+17.9% total tokens for B**, whereas Lab 07's `impact` scenario reports **-33.7% total tokens for B**.

This is not evidence that one result is invalid. The two experiments changed the prompt/output contract:

- Lab 05 used separate markdown sections and a more open-ended response contract;
- Lab 07 used a strict JSON-only schema and was embedded in an explicit task-shape ladder.

Therefore, the economic behavior of an agent is influenced not only by the semantic tool but also by the task contract and output format. The stable signal across both experiments is the correctness/repeatability advantage of semantic-first navigation on the broad structural task.

A stronger external claim should separate:

1. the effect of Rubydex semantic navigation;
2. the effect of a constrained structured output contract;
3. their interaction.

## Methodology notes

- Repository, revision, target, model, reasoning level, and fresh-runner isolation were held constant across the five task shapes.
- Each scenario had three independent samples per condition.
- B includes Rubydex startup/indexing inside measured time.
- Structural correctness is deterministic set equality against the corrected frozen ground truth.
- Three samples are useful for exposing stochastic behavior but are not a publication-grade statistical estimate.
- Estimated cost comes from the harness price table and should be revalidated against current model pricing before publication.
- Full per-sample answers, scores, logs, and token usage remain attached to the GitHub Actions runs.
