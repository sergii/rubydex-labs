# Rubydex Labs

Hands-on experiments for understanding what [Shopify Rubydex](https://github.com/Shopify/rubydex) changes in a real Ruby/Rails development workflow.

The repository is intentionally built as a controlled experiment. The same Rails codebase is used for both sides of every comparison. The only variable we change is the analysis/navigation capability available to the developer or coding agent.

## What we want to learn

Rubydex turns a Ruby workspace into a queryable semantic graph. These labs test two concrete claims:

1. **Structural checks** - whole-codebase rules can be expressed statically instead of booting Rails and inspecting runtime state.
2. **Agent navigation** - a coding agent with semantic code intelligence can inspect fewer files, make fewer search calls, and miss fewer references than an agent using text search alone.

This repository is not a Rubydex tutorial and is not intended to prove that Rubydex wins every task. Tiny or text-local tasks should often show little or no benefit. We want to find the boundary where semantic analysis becomes materially useful.

## Labs

### Lab 01 - Structural linting

Compare two implementations of the same architecture invariant:

> A class must never have both `LegacyFulfillment` and `ModernFulfillment` in its ancestor chain.

The fixture intentionally creates the conflict transitively across files. The control implementation boots Rails, eager-loads the application, and inspects Ruby ancestors at runtime. The treatment implementation asks the Rubydex graph the same structural question without booting the application.

See [`labs/01-structural-linting/README.md`](labs/01-structural-linting/README.md).

### Lab 02 - Agent navigation

Give two fresh coding-agent sessions exactly the same task:

> Rename `Inventory::Reservation` to `Inventory::Allocation` and update every real reference without changing the unrelated `Admin::Reservation`.

The fixture contains relative constant lookup, fully qualified references, inheritance, and deliberate textual noise.

Control:

```text
rg / grep -> read files -> infer relationships -> edit
```

Treatment:

```text
Rubydex semantic query -> read relevant files -> edit
```

See [`labs/02-agent-navigation/README.md`](labs/02-agent-navigation/README.md).

## Repository layout

```text
.
├── app/                         # Shared Rails fixture
├── config/                      # Minimal Rails application
├── labs/
│   ├── 01-structural-linting/
│   └── 02-agent-navigation/
├── rubydex_linter/rules/        # Custom Rubydex structural rules
├── scripts/                     # Reproducible experiment helpers
├── test/structural/             # Runtime control checks
├── benchmarks/                  # Result templates and experiment notes
└── rubydex.toml
```

## Experimental rule

Do **not** modify the fixture between the control and treatment runs of the same experiment.

For the agent benchmark, use `scripts/prepare-agent-fixture` to create isolated workspaces without the repository's explanatory documentation. Do not let the treatment session see notes, transcripts, or patches from the control session.

## Metrics

Record at least:

| Metric | Why it matters |
| --- | --- |
| Correct final result | A faster wrong answer is not useful |
| Real references found | Measures semantic recall |
| False-positive references | Measures search noise |
| Files inspected | Proxy for exploration cost |
| Search/tool calls | Proxy for interaction overhead |
| Tokens used | Direct agent cost/context pressure |
| Wall-clock duration | User-facing latency |
| Time to first correct hypothesis | How quickly the agent forms the right model |

Use [`benchmarks/run-template.md`](benchmarks/run-template.md) for each run.

## Setup

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

Run the runtime structural check:

```bash
bundle exec rails test test/structural/no_conflicting_fulfillment_mixins_test.rb
```

Start the Rubydex MCP server for an AI client:

```bash
bundle exec rdx mcp
```

For clients that support command-based MCP configuration, configure the project-local server command as `bundle exec rdx mcp`.

## References

- [Introducing Rubydex linter: structural checks for Ruby projects](https://railsatscale.com/2026-09-08-introducing-rubydex-linter-structural-checks-for-ruby-projects/)
- [One engine, many tools - Introducing Rubydex](https://railsatscale.com/2026-05-12-one-engine-many-tools/)
- [Shopify/rubydex](https://github.com/Shopify/rubydex)

## Status

This is an experiment repository. Rubydex itself is evolving quickly, and these labs should be updated as its graph, linter, and MCP APIs evolve.
