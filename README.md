# Rubydex Labs

Hands-on experiments for understanding what [Shopify Rubydex](https://github.com/Shopify/rubydex) changes in a real Ruby/Rails development workflow.

The repository is intentionally built as a controlled experiment. The same codebase and task are used for both sides of each comparison. The main variable is the analysis/navigation capability available to the coding agent.

## What we want to learn

Rubydex turns a Ruby workspace into a queryable semantic graph. These labs test concrete claims:

1. **Structural checks** - whole-codebase rules can be expressed statically instead of booting Rails and inspecting runtime state.
2. **Agent navigation** - a coding agent can use semantic code intelligence to resolve declarations and references deterministically.
3. **Scaling** - semantic navigation should become more valuable as same-named declarations, lexical ambiguity, and textual noise grow.
4. **Real-codebase impact mapping** - semantic structure can reduce the cost of building a useful pre-change mental model in a mature Rails monolith.
5. **Consequence X-Ray** - semantic code evidence and explicit architecture knowledge can be measured separately for their contribution to impact, risk, verification, and policy reasoning.
6. **Task-shape boundary** - semantic-first navigation should pay mainly for repository-wide relationship-set tasks, not every lookup.
7. **Evidence routing** - the system should learn when to escalate from ordinary source navigation to deterministic semantic evidence instead of loading semantic context everywhere or leaving tool choice entirely to model whim.

This repository is not a Rubydex tutorial and is not intended to prove that Rubydex wins every task. Tiny or text-local tasks may show little or no benefit. We want to find the boundary where semantic analysis becomes materially useful and the cheapest reliable way to select it.

## Labs

### Lab 01 - Structural linting

Compare two implementations of the same architecture invariant:

> A class must never have both `LegacyFulfillment` and `ModernFulfillment` in its ancestor chain.

See [`labs/01-structural-linting/README.md`](labs/01-structural-linting/README.md).

### Lab 02 - Agent navigation

Rename `Inventory::Reservation` to `Inventory::Allocation` without touching the unrelated `Admin::Reservation`.

The A/B/C runs compare text-only navigation, Rubydex-available navigation, and required semantic-first navigation.

See [`labs/02-agent-navigation/README.md`](labs/02-agent-navigation/README.md).

### Lab 03 - Discovery scaling

Isolate semantic discovery from editing and runtime verification with generated same-name and lexical-resolution noise.

See [`labs/03-discovery-scaling/README.md`](labs/03-discovery-scaling/README.md).

### Lab 04 - Real Discourse reference discovery

Run exact constant-reference discovery against a pinned real `discourse/discourse` revision. The target is `Categories::Types::Base`; ground truth is frozen before A/B measurement.

See [`labs/04-real-discourse/README.md`](labs/04-real-discourse/README.md).

### Lab 05 - Real Discourse impact map

Build a pre-change engineering impact map for `Categories::Types::Base`: named descendants, production users, plugin extensions, direct specs, and a compact read-first set.

See [`labs/05-real-impact-map/README.md`](labs/05-real-impact-map/README.md).

### Lab 06 - X-Ray consequence analysis

Analyze a proposed change that bypasses an asynchronous payment-capture boundary and compare source-only, Rubydex semantic-first, and Rubydex + architecture knowledge + skill conditions.

The output is deliberately consequence-oriented: impacted flows/components, operational risks, verification scenarios, explicit policy violations, and a deploy recommendation.

See [`labs/06-xray-impact/README.md`](labs/06-xray-impact/README.md).

### Lab 07 - Task-shape boundary

Run different engineering task shapes against the same pinned Discourse target to find where semantic-first navigation actually pays.

The key boundary is between cheap/local lookup tasks and repository-wide relationship-set or impact-map tasks. On the impact task, forced semantic-first navigation reached `3/3` exact versus `1/3` ordinary navigation in the recorded run while materially reducing context cost.

See [`labs/07-task-shape-boundary/README.md`](labs/07-task-shape-boundary/README.md).

### Lab 08 - Autonomous semantic escalation

Test whether the agent will choose Rubydex by itself on the real Discourse monolith, then add a minimal decision policy without forcing semantic-first behavior.

The recorded run shows that optional availability alone produced `0/3` Rubydex-using runs. The escalation policy produced `1/3` Rubydex-using runs and substantially reduced aggregate navigation/context cost, which motivates an explicit evidence-routing layer rather than either `semantic-first everywhere` or fully unconstrained model tool choice.

See [`labs/08-autonomous-semantic-escalation/README.md`](labs/08-autonomous-semantic-escalation/README.md) and [`benchmarks/results/2026-09-13-lab-08-autonomous-semantic-escalation.md`](benchmarks/results/2026-09-13-lab-08-autonomous-semantic-escalation.md).

## Primary benchmark path: GitHub Actions

Publishable Labs 04/05 runs use the `Rubydex benchmark` workflow. Later labs use dedicated workflows so each experiment can preserve its own conditions and scoring contract.

For Labs 04/05, each A/B sample gets its own fresh GitHub-hosted `ubuntu-latest` VM. The default run is:

```text
3 x A - text/source navigation
3 x B - Rubydex semantic-first
```

For Lab 06, the default run is:

```text
3 x A - source only
3 x B - Rubydex semantic-first
3 x C - Rubydex + architecture knowledge + skill
```

For Lab 08, the default run is:

```text
3 x D - source navigation
3 x E - identical prompt + optional Rubydex
3 x F - optional Rubydex + minimal semantic-escalation policy
```

The jobs run independently and do not share a Rubydex index, Codex home, filesystem page cache, or local background processes.

The workflows use the official `openai/codex-action@v1`, an `OPENAI_API_KEY` GitHub Actions secret, `drop-sudo`, and a read-only Codex permission profile.

Setup and usage for Labs 04/05:

[`benchmarks/GITHUB_ACTIONS.md`](benchmarks/GITHUB_ACTIONS.md)

Manual runs are available from GitHub Actions, including the base benchmark, X-Ray benchmark, task-shape benchmark, and autonomous-escalation benchmark workflows.

The Labs 04/05 benchmark can also be triggered by changing:

```text
benchmarks/requests/current.json
```

on `main`. Later commit-triggered experiments keep their own request files under `benchmarks/requests/`.

## What the workflows record

Per sample, depending on the lab:

- final answer;
- model / reasoning / condition / repeat metadata;
- exact correctness scoring against frozen ground truth;
- Codex process elapsed time;
- input tokens;
- cached and uncached input tokens;
- output tokens;
- reasoning output tokens;
- total tokens;
- estimated API cost when pricing is known to the aggregator;
- navigation/tool-use metrics such as shell searches and Rubydex MCP calls for routing experiments.

The aggregate jobs write median metrics to the GitHub Actions Step Summary and upload machine-readable and Markdown report artifacts.

## Repository layout

```text
.
├── .github/workflows/                    # Independent benchmark workflows
├── app/                                  # Shared synthetic Rails fixture
├── config/                               # Minimal Rails application
├── labs/                                 # Lab protocols, prompts, ground truth
├── rubydex_linter/rules/                 # Custom Rubydex structural rules
├── scripts/                              # Local and CI runner/scoring helpers
├── test/structural/                      # Runtime control checks
├── benchmarks/
│   ├── requests/                         # Commit-triggered benchmark requests
│   ├── results/                          # Recorded experiment results
│   └── GITHUB_ACTIONS.md                 # Labs 04/05 CI benchmark documentation
└── rubydex.toml
```

## Experimental rules

Do not modify a fixture or frozen external revision between control and treatment runs of the same experiment.

Do not expose frozen ground truth to the benchmark prompt or agent workspace as task guidance.

Keep model and reasoning effort identical between compared conditions.

Use multiple independent samples for claims about cost or latency. Prefer median values over one-off runs.

Treat external repository source as untrusted input. Never place API keys in source files, prompts, benchmark request files, issues, or logs.

Do not attribute a correctness difference to a tool merely because that tool was configured. Tool-effect claims require observed tool calls and consumed evidence.

## Local setup and debugging

The repository pins Ruby 3.4.8. Rubydex itself supports Ruby 3.2+.

Install dependencies:

```bash
bundle install
```

Inspect the Rubydex graph:

```bash
bundle exec rdx query --schema
bundle exec rdx query 'MATCH (c:Class) RETURN c.name'
```

Run the Rubydex linter:

```bash
bundle exec rdx lint
```

Start the Rubydex MCP server:

```bash
bundle exec rdx mcp
```

Local `bin/...` runners remain available for debugging harness changes, but fresh GitHub-hosted samples are the primary measurement path for publishable benchmark claims.

## References

- [Introducing Rubydex linter: structural checks for Ruby projects](https://railsatscale.com/2026-09-08-introducing-rubydex-linter-structural-checks-for-ruby-projects/)
- [One engine, many tools - Introducing Rubydex](https://railsatscale.com/2026-05-12-one-engine-many-tools/)
- [Shopify/rubydex](https://github.com/Shopify/rubydex)

## Status

This is an experiment repository. Rubydex itself is evolving quickly, and these labs should be updated as its graph, linter, MCP APIs, and agent integrations evolve.
