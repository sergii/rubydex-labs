# Running Lab 02 with Codex

Use two fresh Codex sessions with the same model and reasoning level. The launchers inherit your existing Codex configuration, so if you use `Standard`, use it for both runs.

From the repository root:

```bash
bin/run-lab-a
```

Lab A prepares a clean control workspace at `/tmp/rubydex-lab-a`, removes Rubydex from the project fixture, explicitly disables the `rubydex` MCP entry for that Codex invocation, creates a Git baseline, and starts Codex with the canonical task.

After Lab A is complete and you have exited Codex, run:

```bash
bin/run-lab-b
```

Lab B prepares a fresh semantic workspace at `/tmp/rubydex-lab-b`, verifies Rubydex, enables a project-specific Rubydex MCP server only for that Codex invocation, creates the same Git baseline, and starts Codex with the exact same canonical task.

Dependency setup happens before timing starts. When each Codex session exits, the launcher prints elapsed session time and changed files and writes a patch to `/tmp/rubydex-lab-a.patch` or `/tmp/rubydex-lab-b.patch`.

Do not reuse a Codex conversation between A and B, and do not show the Lab A transcript or patch to Lab B.
