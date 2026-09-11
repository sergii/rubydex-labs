# Lab 01 result - Structural linting

Date: 2026-09-12

## Scenario

Both implementations check the same invariant:

> A class must not have both `LegacyFulfillment` and `ModernFulfillment` in its ancestor chain.

The fixture contains one intentional transitive violation in `Warehouse::StockMoveProcessor`.

## Environment

- Same repository state for both runs
- Same local machine
- Rails fixture with dependencies installed
- Commands executed consecutively from the repository root

## Runtime Rails check

Command:

```bash
time bundle exec rails test \
  test/structural/no_conflicting_fulfillment_mixins_test.rb
```

Result:

```text
Failure:
NoConflictingFulfillmentMixinsTest#test_no_class_has_both_fulfillment_implementations_in_its_ancestor_chain:
Classes with conflicting fulfillment mixins: Warehouse::StockMoveProcessor.
Expected [Warehouse::StockMoveProcessor] to be empty.

Finished in 0.136658s
1 runs, 2 assertions, 1 failures, 0 errors, 0 skips
bundle exec rails test   0.89s user 0.50s system 79% cpu 1.755 total
```

Outcome: correct. The runtime check booted Rails, eager-loaded the application, inspected class ancestors, and found the intended offender.

## Rubydex structural linter

Command:

```bash
time bundle exec rdx lint
```

Result:

```text
Indexing workspace... finished in 247.1ms
Resolving graph... finished in 106.33ms
Linting...

app/services/warehouse/stock_move_processor.rb:2:9: error: NoConflictingFulfillmentMixins: `Warehouse::StockMoveProcessor` must not use both fulfillment implementations.

2972 files inspected, 1 offense detected: 1 error, 0 warnings, 0 info, 0 hints
bundle exec rdx lint  0.80s user 0.46s system 197% cpu 0.640 total
```

Outcome: correct. Rubydex found the same transitive structural violation without booting the Rails application.

## Comparison

| Metric | Rails runtime | Rubydex |
| --- | ---: | ---: |
| Correct offender found | yes | yes |
| Wall-clock time | 1.755 s | 0.640 s |
| Relative wall-clock | 1.00x | 0.365x |
| Speedup | baseline | ~2.74x |
| Explicit application boot | yes | no |
| Whole-workspace semantic indexing | no | yes |
| Files reported inspected | n/a | 2,972 |

Rubydex indexing plus resolution took about 353 ms internally (`247.1 + 106.33 ms`). The remaining wall-clock time includes process startup and lint execution.

## Interpretation

This run demonstrates correctness of the experiment and a meaningful wall-clock advantage for Rubydex on this fixture. It does **not** establish a general 2.74x speedup for Rails projects.

Important caveats:

- This fixture is intentionally small.
- Rails process startup is a significant part of the runtime-control cost.
- Rubydex indexed project dependencies as part of the workspace, which makes the 0.640 s result notable but not directly comparable to Rails' internal test duration.
- Repeated warm/cold runs are needed before making performance claims.
- The more important distinction is architectural: the Rails control discovers the relationship at runtime after eager loading, while Rubydex derives it statically from the semantic graph.

## Next experiment

Lab 02 compares coding-agent navigation on the exact same rename task:

- control: text/file navigation only
- treatment: Rubydex MCP semantic navigation

Both runs should use isolated fixture directories and fresh agent sessions.