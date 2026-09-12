# Scout task - real Discourse codebase

This is a research/scouting run, not an A/B benchmark measurement.

Use the Rubydex MCP as the primary source of semantic information.

Target declaration:

`Categories::Types::Base`

Do the following:

1. Call `codebase_stats` and report the indexed codebase statistics.
2. Resolve `Categories::Types::Base` with `get_declaration`.
3. Call `find_constant_references` for `Categories::Types::Base` with a limit high enough to return the complete set.
4. Return every resolved reference as `path:line`, sorted by path then line.
5. Report the total reference count.
6. Use `search_declarations` for the exact unqualified name `Base` and briefly summarize how many unrelated same-named declarations are visible. Do not enumerate hundreds of declarations in the final answer; a count/sample is enough.
7. Read source only narrowly where needed to spot-check interesting cases, especially unqualified references.

Do not edit files. Do not run Rails or tests. Do not install project dependencies. Do not use broad text search to establish the target reference set; the purpose of this scout is to capture Rubydex's semantic result on the pinned real codebase.
