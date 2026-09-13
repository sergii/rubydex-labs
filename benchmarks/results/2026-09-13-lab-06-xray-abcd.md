# Lab 06 - X-Ray consequence benchmark, A/B/C/D

Date: 2026-09-13

GitHub Actions run: https://github.com/sergii/rubydex-labs/actions/runs/34763682406

Model: `gpt-5.6-luna`
Reasoning: `medium`
Samples: 3 per condition, each on a fresh GitHub-hosted VM

## Conditions

- A - source-only repository navigation
- B - source + Rubydex semantic-first navigation
- C - source + Rubydex + explicit architecture knowledge + targeted skill
- D - source + explicit architecture knowledge + targeted skill, no Rubydex

The fixture models a proposed change from queued payment capture to a synchronous call. The deterministic scorer measures impacted flows/components, operational risks, verification scenarios, explicit policy IDs, and deploy recommendation.

## Results

| Condition | Impact recall | Impact precision | Risk recall | Risk precision | Verification recall | Policy recall | Median time | Median tokens | Median est. cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A - text | 85.7% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 19.3 s | 34,527 | $0.0040 |
| B - Rubydex | 85.7% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 34.2 s | 143,428 | $0.0090 |
| C - Rubydex + knowledge | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 19.8 s | 57,298 | $0.0058 |
| D - knowledge only | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 15.7 s | 32,871 | $0.0038 |

Per-sample consequence exact / knowledge exact:

- A: 0/3 / 0/3
- B: 0/3 / 0/3
- C: 2/3 / 3/3
- D: 2/3 / 3/3

Per-sample total tokens:

- A: 25,450; 35,480; 34,527
- B: 110,801; 143,428; 174,443
- C: 57,298; 54,951; 71,774
- D: 32,938; 24,790; 32,871

## Main result

On this controlled fixture, D matched C on every median correctness metric while using materially fewer tokens and less wall-clock time. The explicit architecture knowledge and targeted skill were sufficient to reach 100% median impact recall and 100% policy recall without Rubydex.

Compared with C, D reduced median total tokens from 57,298 to 32,871 (about 43% lower) and median elapsed time from 19.8 s to 15.7 s (about 21% lower). D was also slightly cheaper than source-only A in this run while being more correct on impact and policy.

## Interpretation

This strengthens the hypothesis that the primary missing input for human-facing X-Ray consequence reasoning is system knowledge: architecture intent, policy, risk vocabulary, and targeted procedural guidance. More detailed semantic code structure was not the bottleneck in this small fixture.

Rubydex remains useful as a deterministic evidence source. However, forcing semantic-first navigation everywhere appears counterproductive here. A better design is likely selective semantic lookup: invoke Rubydex only when the model needs a deterministic fact that ordinary source navigation cannot establish cheaply or reliably.

## Important limitations

This is still a small synthetic fixture. Risk and verification already saturate at 100% in A, so those dimensions cannot reveal additional semantic-navigation value. The repository has little lexical ambiguity, shallow inheritance, and a narrow blast radius.

Therefore this run does not support a general claim that Rubydex is unnecessary. It supports a narrower claim: for this X-Ray task, explicit knowledge contributes more value than always-on semantic navigation.

## Next hypothesis

The next useful benchmark should make semantic ambiguity the hard part while keeping company knowledge fixed. Candidate fixtures should include reopened classes, indirection through modules, inheritance, aliases/delegation, misleading lexical matches, and a larger codebase. Then compare:

- D - source + knowledge
- E - source + knowledge + selective Rubydex, with no requirement to use it

The question becomes not whether Rubydex should always be present, but when deterministic semantic evidence is worth asking for.
