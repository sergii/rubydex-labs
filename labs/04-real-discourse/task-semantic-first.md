# Task: exact constant-reference discovery in Discourse

Work only in the checked-out repository. Do not edit files, run Rails, run tests, install dependencies, or change repository state.

Find every Ruby constant reference that resolves to the declaration `Categories::Types::Base`.

Before broad text search or reading candidate source files:

1. use Rubydex to resolve `Categories::Types::Base`;
2. use Rubydex to retrieve its resolved constant references;
3. treat that semantic result as the primary discovery evidence;
4. read only narrowly selected source files when useful for explanation or spot-checking.

Return:

1. the declaration location as `path:line`;
2. every real constant reference as one `path:line` per line, sorted by path then line;
3. a concise explanation of how semantic resolution excluded unrelated constants named `Base`, comments/strings, and other textual matches.

Be complete, but stop once you have enough evidence to give the exact answer.
