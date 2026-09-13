# Lab 07 - Rubydex on demand

## Goal

Test whether an agent that already has explicit architecture knowledge benefits from having Rubydex available **on demand**, without being instructed to use it.

The benchmark compares:

```text
D = source + architecture knowledge + skill
E = source + architecture knowledge + skill + Rubydex MCP available
```

Condition E is deliberately not semantic-first. The prompt never tells the agent to call Rubydex. The agent decides whether semantic evidence is useful.

## Why a harder fixture

Lab 06 showed that, on a small straightforward fixture, architecture knowledge produced the X-Ray value while forced Rubydex navigation added cost without improving median correctness.

Lab 07 therefore adds ambiguity that plain lexical search handles poorly:

- inherited behavior;
- delegation through a facade;
- method aliases;
- a class reopened in another file;
- similarly named decoy classes;
- misleading string/comment matches;
- an indirect call site whose dependency is easier to establish semantically.

## Hypothesis

If E beats D on correctness with acceptable overhead, Rubydex is valuable as a selective deterministic evidence source. If D and E remain equivalent, then semantic tooling should stay optional for this class of consequence analysis and be reserved for still harder structural tasks.

Each sample runs in a sanitized temporary workspace with the frozen ground truth removed before the measured agent starts.
