You are analyzing the pinned Discourse repository in the current working directory.

Target constant: `Categories::Types::Base`.

Task: build the target's exact structural neighborhood.

Return:
1. the target declaration;
2. every named Ruby subclass definition whose superclass resolves to the target, anywhere in the repository, including specs;
3. every direct production Ruby reference resolving to the target, where production means `app/**` and `plugins/**`.

Rules:
- Do not modify files.
- Do not boot Rails or run the test suite.
- Exclude anonymous `Class.new` descendants.
- Include repeated named subclass definitions at distinct source locations.
- Exclude strings, comments, documentation, specs/tests from the production-reference list, and unresolved same-named constants.
- Descendant entries use `ConstantName | path:line`.
- Reference and declaration entries use exact repository-relative `path:line`.
- Sort arrays lexicographically by path, then line.

Return JSON only, with exactly this shape:

{
  "declaration": "path/to/file.rb:123",
  "named_descendants": [
    "ConstantName | path/to/file.rb:123"
  ],
  "direct_production_references": [
    "path/to/file.rb:123"
  ]
}
