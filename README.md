# Rubydex Labs

Hands-on experiments for understanding what [Shopify Rubydex](https://github.com/Shopify/rubydex) changes in a real Ruby/Rails development workflow.

The repository is intentionally built as a controlled experiment. The same Rails codebase is used for both sides of every comparison. The only variable we change is the analysis/navigation capability available to the developer or coding agent.

## What we want to learn

Rubydex turns a Ruby workspace into a queryable semantic graph. These labs test three concrete claims:

1. **Structural checks** - whole-codebase rules can be expressed statically instead of booting Rails and inspecting runtime state.
2. **Agent navigation** - a coding agent can use semantic code intelligence to resolve declarations and references deterministically.
3. **Scaling** - semantic navigation should become more valuable as same-named declarations, lexical ambiguity, and textual noise grow.

This repository is not a Rubydex tutorial and is not intended to prove that Rubydex wins every task. Tiny or text-local tasks may show little or no benefit. We want to find the boundary where semantic analysis becomes materially useful.

## Labs

### Lab 01 - Structural linting

Compare two implementations of the same architecture invariant:

> A class must never have both `LegacyFulfillment` and `ModernFulfillment` in its ancestor chain.

The fixture intentionally creates the conflict transitively across files. The control implementation boots Rails, eager-loads the application, and inspects Ruby ancestors at runtime. The treatment implementation asks the Rubydex graph the same structural question without booting the application.

See [`labs/01-structural-linting/README.md`](labs/01-structural-linting/README.md).

### Lab 02 - Agent navigation

Rename `Inventory::Reservation` to `Inventory::Allocation` without touching the unrelated `Admin::Reservation`.

The A/B/C runs compare:

```text
A  text-only navigation
B  Rubydex available, agent chooses strategy
C  required semantic-first navigation
```

The first measured runs showed that Rubydex returned the exact seven references immediately, but end-to-end task time was still dominated by the coding agent's source inspection and Rails verification behavior.

See [`labs/02-agent-navigation/README.md`](labs/02-agent-navigation/README.md) and [`benchmarks/results/2026-09-12-lab-02-agent-navigation-abc.md`](benchmarks/results/2026-09-12-lab-02-agent-navigation-abc.md).

### Lab 03 - Discovery scaling

Isolate semantic discovery from editing and runtime verification.

The agent must only identify every reference that resolves to `Inventory::Reservation`. A deterministic fixture generator adds unrelated `Reservation` declarations, unqualified references, inheritance, and literal `"Inventory::Reservation"` strings.

Run the text-only and semantic-first conditions at `small`, `medium`, or `large` scale:

```bash
bin/run-discovery-a medium
bin/run-discovery-b medium
```

See [`labs/03-discovery-scaling/README.md`](labs/03-discovery-scaling/README.md).

## Repository layout

```text
.
├── app/                         # Shared Rails fixture
├── config/                      # Minimal Rails application
├── labs/
│   ├── 01-structural-linting/
│   ├── 02-agent-navigation/
│   └── 03-discovery-scaling/
├── rubydex_linter/rules/        # Custom Rubydex structural rules
├── scripts/                     # Reproducible fixture and runner helpers
├── test/structural/             # Runtime control checks
├── benchmarks/                  # Results and experiment notes
└── rubydex.toml
```

## Experimental rules

Do not modify a fixture between control and treatment runs of the same experiment.

Agent benchmarks use isolated workspaces without this repository's explanatory documentation. Do not share transcripts or patches between conditions before both runs are complete.

Keep model and reasoning effort identical between compared runs.

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
| Time to complete dependency set | Measures navigation efficiency |

Use [`benchmarks/run-template.md`](benchmarks/run-template.md) for manual runs.

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

Start the Rubydex MCP server:

```bash
bundle exec rdx mcp
```

## References

- [Introducing Rubydex linter: structural checks for Ruby projects](https://railsatscale.com/2026-09-08-introducing-rubydex-linter-structural-checks-for-ruby-projects/)
- [One engine, many tools - Introducing Rubydex](https://railsatscale.com/2026-05-12-one-engine-many-tools/)
- [Shopify/rubydex](https://github.com/Shopify/rubydex)

## Status

This is an experiment repository. Rubydex itself is evolving quickly, and these labs should be updated as its graph, linter, and MCP APIs evolve.
