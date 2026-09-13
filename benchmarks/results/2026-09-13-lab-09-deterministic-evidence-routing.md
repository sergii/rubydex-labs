# Lab 09 — deterministic evidence routing

Date: 2026-09-13

GitHub Actions run: https://github.com/sergii/rubydex-labs/actions/runs/34766432545

Model: `gpt-5.6-luna`
Reasoning: `medium`
Samples: 3 per scenario/condition, 45 independent samples total

Repository: `discourse/discourse`
Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
Target: `Categories::Types::Base`

## Research question

Once task shape is known, does deterministic evidence routing outperform both unconstrained optional tooling and a prose-only escalation policy?

The controlled oracle route is:

```text
declaration  -> source
descendants  -> semantic
references   -> semantic
neighborhood -> semantic
impact       -> semantic
```

Conditions:

- **E** — Rubydex available; agent chooses freely.
- **F** — Rubydex available; Lab 08 prose escalation policy guides the agent.
- **G** — deterministic task-shape router selects source-only or required semantic-first evidence before the agent starts.

## Aggregate result

| Condition | Exact | Route correct | Semantic runs | RDX calls | Median sec | Median tokens | Median uncached | Median cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E | 10/15 | 3/15 | 0/15 | 0 | 26.2 | 123,954 | 29,521 | $0.0105 |
| F | 13/15 | 7/15 | 4/15 | 9 | 20.2 | 115,379 | 25,393 | $0.0098 |
| G | **15/15** | **15/15** | **12/15** | 77 | **13.5** | **68,570** | **15,596** | **$0.0054** |

G routed the three declaration samples to source-only and all twelve relationship-set samples to semantic-first evidence. Actual tool traces matched that route in every sample.

Compared with E, G median values were approximately:

- **48% lower elapsed time**;
- **45% fewer total tokens**;
- **47% fewer uncached input tokens**;
- **49% lower estimated API cost**;
- exact correctness improved from `10/15` to `15/15`.

Compared with F, G was approximately:

- **33% faster**;
- **41% fewer total tokens**;
- **39% fewer uncached input tokens**;
- **45% cheaper**;
- exact correctness improved from `13/15` to `15/15`.

## Per-scenario result

| Scenario | Cond | Exact | Route correct | Semantic runs | RDX calls | Median sec | Median tokens | Median cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| declaration | E | 3/3 | 3/3 | 0/3 | 0 | 7.4 | 35,742 | $0.0033 |
| declaration | F | 3/3 | 3/3 | 0/3 | 0 | 6.8 | 36,257 | $0.0034 |
| declaration | G | 3/3 | 3/3 | 0/3 | 0 | **5.5** | **31,579** | **$0.0029** |
| descendants | E | 3/3 | 0/3 | 0/3 | 0 | 26.9 | 210,704 | $0.0132 |
| descendants | F | 1/3 | 0/3 | 0/3 | 0 | 20.2 | 95,416 | $0.0084 |
| descendants | G | **3/3** | **3/3** | **3/3** | 20 | **13.5** | **68,570** | **$0.0054** |
| references | E | 3/3 | 0/3 | 0/3 | 0 | 23.2 | 123,954 | $0.0092 |
| references | F | 3/3 | 2/3 | 2/3 | 3 | 14.4 | 78,331 | $0.0063 |
| references | G | **3/3** | **3/3** | **3/3** | 9 | **11.9** | **52,920** | **$0.0046** |
| neighborhood | E | 0/3 | 0/3 | 0/3 | 0 | 26.3 | 103,723 | $0.0089 |
| neighborhood | F | 3/3 | 1/3 | 1/3 | 3 | 28.2 | 126,772 | $0.0109 |
| neighborhood | G | **3/3** | **3/3** | **3/3** | 24 | **18.9** | **71,330** | **$0.0061** |
| impact | E | 1/3 | 0/3 | 0/3 | 0 | 42.5 | 176,732 | $0.0147 |
| impact | F | 3/3 | 1/3 | 1/3 | 3 | 39.3 | 190,792 | $0.0159 |
| impact | G | **3/3** | **3/3** | **3/3** | 24 | **32.9** | **103,889** | **$0.0105** |

## What this supports

1. **The task-shape crossover is actionable.** The source route remains appropriate for declaration lookup; relationship-set tasks benefit from semantic-first routing.
2. **Optional availability is not enough.** E used Rubydex in `0/15` samples even though it was available.
3. **A prose policy improves behavior but remains stochastic.** F selected the oracle route in only `7/15` samples and actually used Rubydex in `4/15`.
4. **Routing before the agent is materially stronger.** G achieved `15/15` exact and `15/15` route adherence while roughly halving context/cost versus E.
5. **The product metric should be evidence-path quality, not Rubydex usage.** G deliberately avoided Rubydex for all declaration samples.

## Important limitation

G is an **oracle task-shape router**. It receives the controlled scenario label; it does not infer task shape from raw natural-language requests. Therefore Lab 09 proves the value of correct routing, not that production routing is solved.

This is useful separation of concerns:

```text
Lab 07 -> discover the crossover
Lab 08 -> show autonomous selection is unreliable
Lab 09 -> measure the upper bound of correct routing
Lab 10 -> infer the route from raw engineering requests
```

## Product implication

The architecture now has experimental support for an explicit evidence router in front of the engineering agent:

```text
engineering request
        |
        v
 task-shape classifier
        |
        v
 evidence router
   /          \
source      semantic
   \          /
    narrowed evidence
          |
          v
       agent
          |
          v
    consequence
```

Rubydex should be treated as a deterministic semantic evidence backend selected when the request depends on repository-wide relationship sets, not as permanent context and not as an optional tool the model is expected to remember to use.

## Next experiment

Lab 10 should remove the scenario label from the router. Feed it raw natural-language engineering requests and require a small classifier to choose among evidence classes such as:

```text
SOURCE_LOCAL
SEMANTIC_RELATIONSHIP_SET
RUNTIME_BEHAVIOR
ARCHITECTURE_KNOWLEDGE
```

Then compare the classifier's route with the Lab 07/09 oracle route and measure downstream correctness, cost, latency, and misrouting cost. This turns the current oracle architecture into a candidate production routing layer.
