You are analyzing the pinned Discourse repository in the current working directory.

Target constant: `Categories::Types::Base`.

Task: enumerate every named Ruby subclass definition whose superclass resolves to this target constant, anywhere in the repository, including production code, plugins, and specs.

Rules:
- Do not modify files.
- Do not boot Rails or run the test suite.
- Exclude the target declaration itself.
- Exclude anonymous `Class.new` descendants.
- Include repeated definitions of the same constant when they occur at distinct source locations.
- Each entry must be `ConstantName | path:line`, using the exact repository-relative definition line.
- Sort entries lexicographically by path, then line.

Return JSON only, with exactly this shape:

{
  "named_descendants": [
    "ConstantName | path/to/file.rb:123"
  ]
}
