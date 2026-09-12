# Task: build a pre-change impact map in Discourse

Work only in the checked-out repository. Do not edit files, run Rails, run tests, install dependencies, or change repository state.

You are preparing to change the implementation of `Categories::Types::Base`. Before touching code, build a compact impact map.

Return these sections exactly:

## Declaration

Return the target declaration as one `path:line`.

## Descendants

Return every named descendant/subclass of `Categories::Types::Base` that you can establish from the repository, one line each as:

```text
ConstantName | path:line
```

Sort by constant name.

## Direct production references

Return every real Ruby constant reference to `Categories::Types::Base` outside `spec/` and `test/`, one `path:line` per line, sorted. Include references inside the target file itself if they resolve to the target. Do not include the declaration, comments, strings, or unrelated `Base` constants.

## Plugin extensions

Return plugin-owned classes that inherit from or structurally extend `Categories::Types::Base`, one line each as:

```text
ConstantName | path:line
```

## Direct-reference spec files

Return each unique spec/test file containing a real constant reference to the target, one path per line, sorted. Do not infer unrelated tests merely from names.

## Read-first set

Choose at most 12 files an engineer should read first before changing `Categories::Types::Base`. Prefer the smallest useful set that covers the target implementation, direct core subclass/usage behavior, plugin extension behavior, and representative direct specs.

Return one line per file as:

```text
path | short reason
```

Use normal repository navigation and source inspection. Be complete on the structural sets, but stop once you have enough evidence to give the impact map. Do not use Rubydex or any semantic-index tool.