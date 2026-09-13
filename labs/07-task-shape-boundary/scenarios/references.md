You are analyzing the pinned Discourse repository in the current working directory.

Target constant: `Categories::Types::Base`.

Task: enumerate every direct production Ruby reference that semantically resolves to this target constant.

For this benchmark, production code means `app/**` and `plugins/**`; exclude `spec/**`, `test/**`, comments, strings, documentation, and unresolved same-named constants.

Rules:
- Do not modify files.
- Do not boot Rails or run the test suite.
- Include subclass declaration lines when their superclass reference resolves to the target.
- Include references from the target implementation itself when they are real resolved constant references.
- Each entry must be an exact repository-relative `path:line`.
- Sort entries lexicographically by path, then line.

Return JSON only, with exactly this shape:

{
  "direct_production_references": [
    "path/to/file.rb:123"
  ]
}
