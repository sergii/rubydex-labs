You are analyzing the pinned Discourse repository in the current working directory.

Target constant: `Categories::Types::Base`.

Task: build a pre-change structural impact map for this target.

Return:
1. the target declaration;
2. every named Ruby subclass definition whose superclass resolves to the target, anywhere in the repository, including specs;
3. every direct production Ruby reference resolving to the target, where production means `app/**` and `plugins/**`;
4. the plugin-defined named subclasses from item 2;
5. every spec file that directly contains a resolved reference to the target;
6. a bounded read-first set of at most 12 Ruby files a senior engineer should inspect before changing the target, with a concise reason for each file.

Rules:
- Do not modify files.
- Do not boot Rails or run the test suite.
- Exclude anonymous `Class.new` descendants from `named_descendants`.
- Include repeated named subclass definitions at distinct source locations.
- Exclude strings, comments, documentation, specs/tests from the production-reference list, and unresolved same-named constants.
- Descendant and plugin entries use `ConstantName | path:line`.
- Reference and declaration entries use exact repository-relative `path:line`.
- Spec entries are repository-relative file paths only.
- The read-first set must contain repository-relative Ruby file paths plus short evidence-based reasons; do not exceed 12 files.
- Sort structural arrays lexicographically by path, then line.

Return JSON only, with exactly this shape:

{
  "declaration": "path/to/file.rb:123",
  "named_descendants": [
    "ConstantName | path/to/file.rb:123"
  ],
  "direct_production_references": [
    "path/to/file.rb:123"
  ],
  "plugin_extensions": [
    "ConstantName | plugins/path/to/file.rb:123"
  ],
  "direct_reference_spec_files": [
    "spec/path/to/file_spec.rb"
  ],
  "read_first": [
    {"path": "path/to/file.rb", "reason": "why this file matters"}
  ]
}
