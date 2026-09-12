# Rubydex Labs

Hands-on experiments for understanding what [Shopify Rubydex](https://github.com/Shopify/rubydex) changes in a real Ruby/Rails development workflow.

The repository is intentionally built as a controlled experiment. The same codebase and task are used for both sides of each comparison. The main variable is the analysis/navigation capability available to the coding agent.

## What we want to learn

Rubydex turns a Ruby workspace into a queryable semantic graph. These labs test concrete claims:

1. **Structural checks** - whole-codebase rules can be expressed statically instead of booting Rails and inspecting runtime state.
2. **Agent navigation** - a coding agent can use semantic code intelligence to resolve declarations and references deterministically.
3. **Scaling** - semantic navigation should become more valuable as same-named declarations, lexical ambiguity, and textual noise grow.
4. **Real-codebase impact mapping** - semantic structure can reduce the cost of building a useful pre-change mental model in a mature Rails monolith.

This repository is not a Rubydex tutorial and is not intended to prove that Rubydex wins every task. Tiny or text-local tasks may show little or no benefit. We want to find the boundary where semantic analysis becomes materially useful.

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

## Primary benchmark path: GitHub Actions

Publishable Lab 04/05 runs should use the public GitHub Actions workflow rather than a developer laptop.

Each A/B sample gets its own fresh GitHub-hosted `ubuntu-latest` VM. The default run is:

```text
3 × A — text/source navigation
3 × B — Rubydex semantic-first
```

The jobs run independently, with at most two samples in parallel. They do not share a Rubydex index, Codex home, filesystem page cache, or local background processes.

The workflow uses the official `openai/codex-action@v1`, an `OPENAI_API_KEY` GitHub Actions secret, `drop-sudo`, and a read-only Codex permission profile.

Setup and usage:

[`benchmarks/GITHUB_ACTIONS.md`](benchmarks/GITHUB_ACTIONS.md)

A manual run is available from:

```text
GitHub → Actions → Rubydex benchmark → Run workflow
```

The benchmark can also be triggered by changing:

```text
benchmarks/requests/current.json
```

on `main`. This makes automated experiment iteration possible without a local terminal.

## What the workflow records

Per sample:

- final answer;
- model / reasoning / condition / repeat metadata;
- exact correctness scoring against frozen ground truth;
- Codex process elapsed time;
- input tokens;
- cached and uncached input tokens;
- output tokens;
- reasoning output tokens;
- total tokens;
- estimated API cost when pricing is known to the aggregator.

The aggregate job produces median A/B metrics and writes them to the GitHub Actions Step Summary plus a downloadable `benchmark-report` artifact.

## Repository layout

```text
.
├── .github/workflows/benchmark.yml # Ephemeral GitHub benchmark runner
├── app/                            # Shared synthetic Rails fixture
├── config/                         # Minimal Rails application
├── labs/                           # Lab protocols, prompts, ground truth
├── rubydex_linter/rules/           # Custom Rubydex structural rules
├── scripts/                        # Local and CI runner/scoring helpers
├── test/structural/                # Runtime control checks
├── benchmarks/
│   ├── requests/current.json       # Commit-triggered benchmark request
│   ├── results/                    # Recorded experiment results
│   └── GITHUB_ACTIONS.md           # CI benchmark documentation
└── rubydex.toml
```

## Experimental rules

Do not modify a fixture or frozen external revision between control and treatment runs of the same experiment.

Do not expose frozen ground truth to the benchmark prompt or agent workspace as task guidance.

Keep model and reasoning effort identical between compared conditions.

Use multiple independent samples for claims about cost or latency. Prefer median values over one-off runs.

Treat external repository source as untrusted input. Never place API keys in source files, prompts, benchmark request files, issues, or logs.

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

Local `bin/...` runners remain available for debugging harness changes, but fresh GitHub-hosted samples are the primary measurement path for Labs 04 and 05.

## References

- [Introducing Rubydex linter: structural checks for Ruby projects](https://railsatscale.com/2026-09-08-introducing-rubydex-linter-structural-checks-for-ruby-projects/)
- [One engine, many tools - Introducing Rubydex](https://railsatscale.com/2026-05-12-one-engine-many-tools/)
- [Shopify/rubydex](https://github.com/Shopify/rubydex)

## Status

This is an experiment repository. Rubydex itself is evolving quickly, and these labs should be updated as its graph, linter, MCP APIs, and agent integrations evolve.
