# Lab 08 — autonomous semantic escalation

Date: 2026-09-13

GitHub Actions run: https://github.com/sergii/rubydex-labs/actions/runs/34765551350

Model: `gpt-5.6-luna`
Reasoning: `medium`
Samples: 3 per condition, each on a fresh GitHub-hosted VM

Repository: `discourse/discourse`
Revision: `c89b1a0506a3ec0a249b7f23ac86763b358dc177`
Target: `Categories::Types::Base`

## Research question

On a real large Rails repository, will an agent autonomously choose Rubydex when repository-wide semantic relationships matter, and can a minimal decision policy trigger useful escalation without forcing `semantic-first everywhere`?

## Conditions

- **D — source only:** ordinary read-only repository navigation.
- **E — optional Rubydex:** identical prompt to D; Rubydex MCP exists in the environment but the prompt does not mention it.
- **F — escalation policy:** Rubydex remains optional, but the agent receives one rule: use deterministic semantic evidence first when the task depends on repository-wide semantic relationship sets and broad source traversal would be expensive; otherwise use ordinary navigation.

The structural task and frozen ground truth are reused from Lab 07.

## Aggregate result

| Condition | Exact | Desc recall | Ref recall | Plugin recall | Spec recall | RDX runs | RDX total calls | Median shell cmds | Median search cmds | Median sec | Median total tokens | Median uncached | Median est. cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D | 2/3 | 100% | 100% | 100% | 100% | 0/3 | 0 | 8 | 3 | 49.7 | 201,636 | 43,549 | $0.0177 |
| E | 3/3 | 100% | 100% | 100% | 100% | 0/3 | 0 | 8 | 3 | 35.9 | 187,776 | 39,298 | $0.0148 |
| F | 3/3 | 100% | 100% | 100% | 100% | **1/3** | **3** | **6** | **2** | **34.3** | **114,632** | **27,520** | **$0.0113** |

D's one non-exact result still had 100% precision/recall for every relationship set; it missed exactness only on the declaration field. Therefore the structural task was solved very well by all conditions in this run.

## Actual semantic-tool selection

### D

Rubydex unavailable by design.

- semantic runs: `0/3`
- semantic calls: `0`

### E

Rubydex was configured and available, but all three agents ignored it.

- semantic runs: `0/3`
- semantic calls: `0`

Therefore E's `3/3` exact score versus D's `2/3` **must not be attributed to Rubydex evidence**. No E sample consumed semantic-tool output. The difference is compatible with normal stochastic variation and other incidental execution differences.

### F

The minimal decision rule changed behavior, but not deterministically.

- F-r1: `0` Rubydex calls
- F-r2: `0` Rubydex calls
- F-r3: `3` Rubydex calls
  - `get_declaration`
  - `get_descendants`
  - `find_constant_references`

So autonomous semantic escalation happened in **1 of 3** policy-guided runs.

## Per-sample F economics

| Sample | Exact | RDX calls | Shell cmds | Search cmds | Total tokens | Uncached | Sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F-r1 | yes | 0 | 6 | 2 | 100,663 | 26,804 | 30.6 |
| F-r2 | yes | 0 | 9 | 3 | 127,816 | 33,301 | 35.1 |
| F-r3 | yes | **3** | **3** | **1** | 114,632 | 27,520 | 34.3 |

The semantic run had the fewest shell/search commands and used Rubydex exactly as intended: one declaration lookup, one descendant-set query, and one resolved-reference query, followed by narrowed source verification.

However, it was **not** the cheapest or fastest F run. F-r1 solved the task exactly with no semantic calls and fewer tokens/time than F-r3. This matters: Rubydex clearly reduced repository traversal, but on this particular task/model/run that traversal reduction did not translate into the absolute best end-to-end token or latency result.

## Effect of the decision policy

The strongest aggregate difference is not semantic-tool usage itself. It is the F decision policy.

Compared with D, F median values were approximately:

- **43% fewer total tokens** (`114,632` vs `201,636`);
- **37% fewer uncached input tokens** (`27,520` vs `43,549`);
- **31% lower elapsed time** (`34.3s` vs `49.7s`);
- **36% lower estimated API cost** (`$0.0113` vs `$0.0177`);
- fewer shell/search commands.

Compared with E, F used approximately:

- **39% fewer total tokens**;
- **30% fewer uncached input tokens**;
- **24% lower estimated API cost**.

Because two of the three F runs never called Rubydex, these improvements cannot be assigned to semantic evidence alone. The decision rule appears to improve navigation discipline even when the model ultimately stays on source tools.

## What Lab 08 supports

1. **Availability is not selection.** A useful MCP tool can be present on a real monolith and still be ignored in every unconstrained run.
2. **A small decision policy changes agent behavior.** It produced one real semantic escalation and materially lower aggregate navigation/context cost.
3. **The policy is not reliable enough yet.** `1/3` semantic selection is too stochastic for a deterministic engineering workflow.
4. **Semantic evidence can reduce traversal.** The one F run that used Rubydex needed only three shell commands and one text-search command after obtaining deterministic relationship sets.
5. **Semantic tooling is not automatically the cheapest path.** A well-directed source-only run can still beat a semantic run on a task the model happens to solve efficiently.

## Product implication

The evidence now argues against both extremes:

```text
semantic-first everywhere       -> too rigid
agent decides entirely alone    -> too stochastic
```

A stronger architecture is a **tool-selection router / escalation policy**:

```text
                 engineering task
                        |
                        v
                classify task shape
                        |
          +-------------+--------------+
          |                            |
   local/textual task          relationship-set task
          |                            |
          v                            v
     source tools              semantic evidence
                                      |
                                      v
                           narrow source verification
                                      |
                                      v
                                  consequence
```

The router does not need to understand the whole answer. It only needs to recognize when the question depends on repository-wide semantic sets such as descendants, resolved references, reopenings, or broad impact maps.

That is a more defensible product rule than asking the model to remember to use Rubydex:

> Use semantic indexing as an evidence escalation path selected by task shape and uncertainty, not as permanent context and not as a purely optional tool left to model whim.

## Next experiment

Lab 09 should move the decision out of prose and into an explicit lightweight router.

Suggested comparison:

```text
E = optional Rubydex, agent decides
F = prose escalation policy
G = deterministic task-shape router
```

The router can classify the task before the coding agent starts:

- declaration/local lookup -> source or one semantic lookup;
- repository-wide relationship set -> Rubydex first;
- impact map -> Rubydex relationship discovery, then source verification;
- behavioral/runtime question -> runtime/test evidence rather than more static navigation.

Measure correctness, tool-selection accuracy, semantic calls, shell/search commands, uncached context, latency, and cost. The key success metric becomes not "did Rubydex win?" but **"did the system choose the cheapest reliable evidence path?"**
