# Task: build a pre-change impact map in Discourse

Work only in the checked-out repository. Do not edit files, run Rails, run tests, install dependencies, or change repository state.

You are preparing to change the implementation of `Categories::Types::Base`. Before touching code, build a compact impact map.

Before broad text search or reading candidate files, use Rubydex semantic tools to:

1. resolve the target declaration;
2. get its descendants;
3. get all resolved constant references.

Use those semantic results as the primary evidence for narrowing source reads. Read source only where needed to classify core/plugin/spec usage or justify the read-first set. Do not enumerate unrelated `Base` declarations once the target identity is resolved.

Return these sections exactly:

## Declaration

Return the target declaration as one `path:line`.

## Descendants

Return every named descendant/subclass of `Categories::Types::Base` reported by semantic resolution, one line each as:

```text
ConstantName | path:line
```

Sort by constant name.

## Direct production references

Return every resolved Ruby constant reference to `Categories::Types::Base` outside `spec/` and `test/`, one `path:line` per line, sorted. Include references inside the target file itself if they resolve to the target. Do not include the declaration, comments, strings, or unrelated `Base` constants.

## Plugin extensions

Return plugin-owned classes that inherit from or structurally extend `Categories::Types::Base`, one line each as:

```text
ConstantName | path:line
```

## Direct-reference spec files

Return each unique spec/test file containing a resolved constant reference to the target, one path per line, sorted.

## Read-first set

Choose at most 12 files an engineer should read first before changing `Categories::Types::Base`. Prefer the smallest useful set that covers the target implementation, direct core subclass/usage behavior, plugin extension behavior, and representative direct specs.

Return one line per file as:

```text
path | short reason
```

Be complete on the structural sets, but stop once you have enough semantic and source evidence to give the impact map.