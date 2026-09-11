# Agent task - semantic-first discovery

Find every Ruby constant reference that resolves to `Inventory::Reservation`.

Return each real reference as `path:line`. Separate unrelated constants that are also named `Reservation`.

Before any broad text search or candidate-file reading, use Rubydex MCP to resolve `Inventory::Reservation` and query its resolved constant references. Use those semantic results as the primary evidence. You may use narrow source reads afterward only to verify context.

Do not edit files. Do not run Rails or tests. Stop after you have a complete answer.

Briefly explain how you distinguished the target constant from unrelated same-named constants.