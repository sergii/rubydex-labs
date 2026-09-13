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

## Guardrail

G is a routing upper bound. It must not be described as an autonomous classifier. If G wins, the next problem is to build and evaluate a classifier/router that infers task shape from a natural-language engineering request without access to benchmark labels.
