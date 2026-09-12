# Task: exact constant-reference discovery in Discourse

Work only in the checked-out repository. Do not edit files, run Rails, run tests, install dependencies, or change repository state.

Find every Ruby constant reference that resolves to the declaration `Categories::Types::Base`.

Return:

1. the declaration location as `path:line`;
2. every real constant reference as one `path:line` per line, sorted by path then line;
3. a concise explanation of how you distinguished unrelated constants named `Base`, comments/strings, and other textual matches.

Use normal repository navigation and source inspection. Be complete, but stop once you have enough evidence to give the exact answer. Do not use Rubydex or any semantic-index tool.
