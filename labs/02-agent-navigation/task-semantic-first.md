# Agent task - semantic-first condition

Rename the Ruby class `Inventory::Reservation` to `Inventory::Allocation`.

Update every real Ruby reference that resolves to `Inventory::Reservation` and rename its defining file as appropriate.

Do not rename or modify the unrelated `Admin::Reservation` class. Do not change prose, labels, or historical strings merely because they contain the word `Reservation` or the text `Inventory::Reservation`.

Before editing, identify the affected Ruby declarations/references. After editing, summarize what changed and call out anything you intentionally left unchanged.

## Required navigation strategy

Before running any broad repository text search (`rg`, `grep`, or equivalent) or reading candidate source files, use the Rubydex MCP tools to:

1. Resolve the declaration `Inventory::Reservation`.
2. Find all resolved constant references to that declaration.
3. Resolve `Admin::Reservation` and its references so the unrelated constant is explicitly separated.
4. Use those semantic results to decide which source files need inspection.

After that semantic discovery step, read only the files needed to make the change. Text search is allowed afterward for validation, strings, generated names, or other non-semantic checks.

Do not treat Rubydex as proof that edited files have already been re-indexed. Verify the final change using source/runtime checks appropriate for the Rails application.
