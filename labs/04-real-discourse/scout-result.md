# Discourse scout result

Date: 2026-09-12

Repository: `discourse/discourse`

Pinned revision:

```text
c89b1a0506a3ec0a249b7f23ac86763b358dc177
```

Target declaration: `Categories::Types::Base`

The scout is ground-truth preparation, not a benchmark measurement.

## Rubydex graph

```text
files: 15,130
declarations: 137,534
definitions: 145,449
constant references: 453,208
method references: 1,559,344
```

The target resolves to `app/services/categories/types/base.rb:5` and Rubydex returned 21 resolved constant references. The exact frozen reference set is stored in `ground-truth.txt`.

An exact declaration search for the short name `Base` exposed 2,574 visible matches. This creates substantial real-world ambiguity for text-first navigation.

Notable reference shapes include:

- an unqualified lexical reference in core: `Categories::Types::Discussion < Base`
- fully-qualified plugin subclasses using `::Categories::Types::Base`
- spec references using both qualified inheritance and dynamic class creation
- a self-reference inside `app/services/categories/types/base.rb`

## Scout execution metadata

```text
model: gpt-5.6-luna
reasoning: medium
elapsed_seconds: 50
total_tokens: 131,830
input_tokens: 130,030
cached_input_tokens: 109,056
uncached_input_tokens: 20,974
output_tokens: 1,800
reasoning_output_tokens: 737
```

These numbers must not be compared against A/B; the scout performed extra graph/statistics and ambiguity queries specifically to establish ground truth.
