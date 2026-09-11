# Lab 01 - Structural linting

## Question

Can a Rubydex structural rule replace a Rails runtime test that must eager-load the application to inspect a cross-file ancestor relationship?

## Invariant

A class must never have both `LegacyFulfillment` and `ModernFulfillment` anywhere in its ancestor chain.

The fixture violates the invariant indirectly:

```text
Warehouse::StockMoveProcessor
  includes ModernFulfillment
  inherits Warehouse::BaseProcessor
    includes LegacyFulfillment
```

Neither file contains both `include` calls. A file-local AST rule is therefore not enough to establish the violation.

## Control - runtime Rails test

Run:

```bash
time bundle exec rails test test/structural/no_conflicting_fulfillment_mixins_test.rb
```

The test deliberately calls `Rails.application.eager_load!`, enumerates loaded classes, and inspects their Ruby ancestor chains.

Expected result: the test fails and identifies `Warehouse::StockMoveProcessor`.

Record:

- wall-clock duration
- process memory if your measurement tool exposes it
- application boot/eager-load cost
- implementation complexity

## Treatment - Rubydex structural rule

Run:

```bash
time bundle exec rdx lint
```

The rule is in:

```text
rubydex_linter/rules/no_conflicting_fulfillment_mixins.rb
```

It asks Rubydex for classes that have `ModernFulfillment` in their resolved ancestry and then checks whether `LegacyFulfillment` is also an ancestor.

Expected result: the linter fails and reports the same class without booting Rails.

Inspect the rule documentation with:

```bash
bundle exec rdx lint explain NoConflictingFulfillmentMixins
```

## What this lab is actually testing

Do not focus only on absolute speed in this tiny repository. Rails boot is cheap here, while Shopify's motivating case is a very large monolith.

The interesting differences are architectural:

| Runtime test | Rubydex rule |
| --- | --- |
| Needs executable application state | Uses static workspace analysis |
| Needs eager loading for complete class coverage | Indexes the workspace and dependencies |
| Reads Ruby runtime ancestors | Reads resolved semantic ancestors |
| Often couples check cost to application boot cost | Reuses the Rubydex graph used by other tools |

## Follow-up experiments

After the baseline works, scale the fixture to 100, 1,000, and 10,000 generated classes while keeping one transitive violation. Compare how the two approaches scale and separate one-time indexing cost from per-rule cost.
