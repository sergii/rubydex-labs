# Lab 09 — deterministic evidence routing

## Goal

Test the architecture implied by Labs 07–08: choose the evidence backend from task shape before the coding agent starts, instead of forcing semantic-first everywhere or leaving Rubydex selection entirely to model whim.

The benchmark reuses the same pinned `discourse/discourse` revision, target (`Categories::Types::Base`), five task shapes, and frozen ground truth from Lab 07.

## Conditions

```text
E = Rubydex available; agent chooses freely
F = Rubydex available; prose escalation policy guides the agent
G = deterministic task-shape router chooses the evidence path
```

For G the controlled router uses the known scenario label:

```text
declaration  -> source
descendants  -> semantic
references   -> semantic
neighborhood -> semantic
impact       -> semantic
```

This is intentionally an **oracle router**, not a claim that production task classification is solved. Lab 09 measures the upper bound once task shape is known. A later experiment can classify raw user prompts.

## Why this mapping

Lab 07 found the crossover immediately after declaration lookup: source navigation was cheaper for the trivial declaration task, while semantic-first reduced cost/context and/or improved correctness for every relationship-set task. Lab 08 then showed that optional availability was not enough and a prose policy still escalated stochastically.

## Measurements

Per scenario and condition:

- exact structural correctness;
- whether actual tool selection matches the expected route;
- runs with Rubydex calls and total semantic calls;
- shell/search navigation commands;
- elapsed time;
- total and uncached tokens;
- estimated API cost.

The primary question is no longer “does Rubydex win?” It is:

> Does explicit evidence routing recover the cheapest reliable path across different task shapes?

## Observed result

The repeated `3 × 5 scenarios × 3 conditions = 45` sample run strongly favored the routed condition:

| Condition | Exact | Route correct | Semantic runs | Median sec | Median tokens | Median uncached | Median cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E | 10/15 | 3/15 | 0/15 | 26.2 | 123,954 | 29,521 | $0.0105 |
| F | 13/15 | 7/15 | 4/15 | 20.2 | 115,379 | 25,393 | $0.0098 |
| G | **15/15** | **15/15** | **12/15** | **13.5** | **68,570** | **15,596** | **$0.0054** |

G deliberately used source-only navigation for all three declaration samples and semantic-first evidence for all twelve relationship-set samples. Compared with E, G was about 48% faster, used 45% fewer total tokens and 47% fewer uncached tokens, and cost about 49% less while improving exact correctness from `10/15` to `15/15`.

Compared with F, G was about 33% faster, used 41% fewer total tokens and 39% fewer uncached tokens, and cost about 45% less while improving exact correctness from `13/15` to `15/15`.

Full result: [`benchmarks/results/2026-09-13-lab-09-deterministic-evidence-routing.md`](../../benchmarks/results/2026-09-13-lab-09-deterministic-evidence-routing.md).

## Guardrail

G is a routing upper bound. It must not be described as an autonomous classifier. The result demonstrates that **correct evidence routing is valuable**; it does not demonstrate that production task classification is solved.

The next experiment should infer task shape from raw natural-language engineering requests without access to benchmark scenario labels.