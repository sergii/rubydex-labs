# Ground-truth provenance

The frozen 21-reference set in `ground-truth.txt` was produced by the non-timed Rubydex scout against:

```text
discourse/discourse@c89b1a0506a3ec0a249b7f23ac86763b358dc177
```

Target declaration:

```text
Categories::Types::Base
app/services/categories/types/base.rb:5
```

Scout semantic result:

```text
21 resolved constant references
```

The benchmark prompts do not include the count or the frozen reference list. The scoring harness reads `ground-truth.txt` only after each Codex run has completed.

Representative references were spot-checked in source before timing:

- `app/services/categories/types/discussion.rb:5` is the lexical `class Discussion < Base` reference.
- plugin category types use explicit `::Categories::Types::Base` inheritance.
- specs include dynamic `Class.new(Categories::Types::Base)` and direct constant references.

This file documents provenance; it does not claim an independent second implementation verified every one of the 21 references.
