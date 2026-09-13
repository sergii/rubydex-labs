# Lab 05 — real Discourse impact map on fresh GitHub runners

Date: 2026-09-13

## Setup

- Repository under analysis: `discourse/discourse`
- Pinned revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
- Target: `Categories::Types::Base`
- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Samples: 3 per condition
- Each sample ran on a separate fresh GitHub-hosted `ubuntu-latest` VM.
- A: normal repository navigation, no Rubydex MCP.
- B: semantic-first navigation with Rubydex MCP.
- Rubydex MCP startup/indexing remained inside the measured Codex session.
- All samples were read-only and used the official `openai/codex-action` with API-key authentication from GitHub Actions secrets.

Source benchmark workflow run: `34753528889`
Post-run report workflow run: `34753725770`

## Ground-truth correction before repeated runs

The initial semantic scout froze only one `MockCategoryType` subclass definition. Independent fresh-run A/B smoke samples both found another named subclass at:

```text
MockCategoryType | spec/system/simplified_category_creation_spec.rb:24
```

The pinned source confirms `class MockCategoryType < ::Categories::Types::Base` at that location. The scout had rendered that descendant entry as anonymous. The ground truth was therefore corrected before the 3+3 repeated benchmark.

The corrected descendant set contains 6 named subclass definitions across 5 unique constant names.

## Samples

| Sample | Structural exact | Time (s) | Total tokens | Uncached input | Output | Estimated cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-r1 | no | 47.9 | 97,854 | 24,921 | 4,478 | $0.0117 |
| A-r2 | no | 38.5 | 95,960 | 31,685 | 3,402 | $0.0116 |
| A-r3 | no | 35.3 | 118,623 | 28,073 | 3,300 | $0.0113 |
| B-r1 | yes | 37.6 | 111,917 | 29,858 | 2,541 | $0.0106 |
| B-r2 | yes | 34.8 | 115,377 | 23,678 | 2,358 | $0.0094 |
| B-r3 | yes | 47.8 | 152,063 | 30,541 | 3,031 | $0.0121 |

All six runs achieved 5/5 read-first rubric coverage.

## Median A vs B

| Metric | A — text | B — Rubydex | B vs A |
| --- | ---: | ---: | ---: |
| Structural exact | 0/3 | 3/3 | treatment wins |
| Read-first coverage | 5/5 | 5/5 | equal |
| Elapsed seconds | 38.5 | 37.6 | -2.2% |
| Total tokens | 97,854 | 115,377 | +17.9% |
| Input tokens | 93,376 | 113,019 | +21.0% |
| Cached input | 68,455 | 89,341 | +30.5% |
| Uncached input | 28,073 | 29,858 | +6.4% |
| Output tokens | 3,402 | 2,541 | -25.3% |
| Reasoning output | 1,578 | 1,121 | -29.0% |
| Estimated API cost | $0.0116 | $0.0106 | -8.8% |

## Interpretation

Lab 05 changes the conclusion from the narrower constant-reference experiments.

On this multi-part impact-map task, Rubydex did **not** materially reduce wall time or model input. Median latency was nearly equal, and B consumed more total/input tokens. Semantic tool calls and their returned graph data are real context overhead.

The strongest treatment effect was instead **correctness and determinism**:

- text-only A produced no structurally exact answer across three independent fresh VMs;
- semantic-first B produced an exact structural answer in all three independent fresh VMs;
- both conditions produced useful read-first plans with full rubric coverage.

B also emitted less output and less reasoning despite receiving more input context. At the current price assumptions encoded by the harness, estimated median API cost was slightly lower for B, but cost is secondary here and the price table should be revalidated before external publication.

A reasonable claim from this experiment is therefore:

> For a real pre-change Ruby impact-map task on a large production Rails codebase, Rubydex improved structural correctness and repeatability substantially, while latency was effectively unchanged and semantic context introduced additional input-token overhead.

This is more nuanced than “Rubydex always uses fewer tokens.” The benefit depends on task shape: exact reference discovery showed large context savings, while multi-part architectural impact mapping primarily showed an accuracy/reliability benefit.

## Methodology notes

- Fresh VM per sample removes A→B filesystem and Rubydex-index warming effects.
- The repeated run used three independent samples per condition; that is enough to expose stochastic behavior but not enough for a publication-grade statistical estimate.
- A and B used the same model and reasoning level.
- The corrected structural ground truth was frozen before the repeated 3+3 run.
- Final answers, job logs, token usage and report artifacts remain attached to the GitHub Actions runs.
