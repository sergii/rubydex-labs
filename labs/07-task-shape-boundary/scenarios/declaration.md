You are analyzing the pinned Discourse repository in the current working directory.

Target constant: `Categories::Types::Base`.

Task: locate the Ruby declaration that defines this target constant.

Rules:
- Do not modify files.
- Do not boot Rails or run the test suite.
- Report the declaration as an exact repository-relative `path:line`.
- Do not include references, descendants, commentary, or guesses.

Return JSON only, with exactly this shape:

{
  "declaration": "path/to/file.rb:123"
}
