# Scout: semantic impact map for `Categories::Types::Base`

This is a ground-truth collection run, not a benchmark. Work only in the checked-out repository. Do not edit files, run Rails, run tests, install dependencies, or change repository state.

Use Rubydex semantic tools as the primary evidence. Source reads may be used only to classify or spot-check semantic results.

Build a structural impact map for the declaration `Categories::Types::Base`.

Return these sections exactly:

## Declaration

Return the declaration as one `path:line`.

## Descendants

Use Rubydex descendant resolution. Return every named descendant/subclass that Rubydex reports, one line each as:

```text
ConstantName | path:line
```

Sort by constant name. If a reported descendant is defined only in test/spec code, keep it and make that visible by its path.

## Direct production references

Use Rubydex resolved constant references. Return every reference outside `spec/` and `test/`, one `path:line` per line, sorted. Include references inside the target file itself if they resolve to the target. Do not include the declaration.

## Plugin extensions

From descendants and references, identify plugin-owned classes that inherit from or otherwise structurally extend `Categories::Types::Base`. Return one line each:

```text
ConstantName | path:line
```

Only include real Ruby structural extensions, not comments or prose.

## Direct-reference spec files

From the resolved reference set, return each unique spec/test file containing a real reference to the target, one path per line, sorted. Do not infer unrelated tests merely from naming.

## Read-first set

Choose at most 12 files an engineer should read before changing `Categories::Types::Base`. Prefer the smallest useful set that covers:

- the target implementation;
- direct core subclass/usage behavior;
- plugin extension behavior;
- representative direct specs.

For each file, give one short reason. This section is judgment, not exact ground truth.

## Evidence summary

Report:

- total descendants returned by Rubydex;
- total resolved constant references;
- production-reference count after excluding spec/test paths;
- unique direct-reference spec/test file count;
- plugin-extension count.

Be complete on the exact structural sets, but do not broaden into general repository architecture or unrelated textual searches.