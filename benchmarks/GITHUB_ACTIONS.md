# GitHub Actions benchmark runner

The primary benchmark path is now GitHub Actions. Local `bin/...` runners remain useful for debugging, but publishable benchmark samples should come from fresh GitHub-hosted VMs.

## Why

Each A/B sample runs in its own `ubuntu-latest` job, so conditions do not share:

- filesystem page cache;
- a Rubydex index;
- Codex home/config/cache;
- local background processes;
- machine load from the opposite condition.

The default run is three A samples and three B samples with at most two samples executing in parallel.

## Security

The workflow uses `openai/codex-action@v1` with:

- `OPENAI_API_KEY` from GitHub Actions secrets;
- `safety-strategy: drop-sudo`;
- `permission-profile: :read-only`;
- a trusted `codex-home` created by the workflow;
- the Discourse checkout treated as untrusted read-only source input.

Do not put an API key in this repository, benchmark request files, prompts, issue text, or workflow inputs.

## One-time setup

Create an OpenAI API key for the API project you want to use, then add it to the repository as an Actions secret named exactly:

```text
OPENAI_API_KEY
```

GitHub path:

```text
sergii/rubydex-labs
→ Settings
→ Secrets and variables
→ Actions
→ New repository secret
→ Name: OPENAI_API_KEY
→ Secret: <your OpenAI API key>
```

The OpenAI project must have API billing/credits available and access to the selected model.

## Manual run

Open:

```text
GitHub → sergii/rubydex-labs → Actions → Rubydex benchmark → Run workflow
```

Inputs:

- `lab`: `04` or `05`;
- `model`: defaults to `gpt-5.6-luna`;
- `reasoning`: `low`, `medium`, or `high`;
- `repetitions`: `1` or `3` samples per condition.

## Commit-triggered run

Updating this trusted file on `main` automatically starts a benchmark:

```text
benchmarks/requests/current.json
```

Example:

```json
{
  "lab": "05",
  "model": "gpt-5.6-luna",
  "reasoning": "medium",
  "repetitions": 3
}
```

This is useful for automated experiment iteration: change the request, commit it, then inspect the workflow result.

## Outputs

Every sample uploads an artifact containing:

- `final.txt` — final Codex answer;
- `meta.json` — lab, condition, repeat, model, reasoning, and pinned Discourse revision.

Codex runs with `--json`; the aggregate job reads completed sample job logs to recover:

- elapsed Codex process time;
- input tokens;
- cached input tokens;
- uncached input tokens;
- output tokens;
- reasoning output tokens;
- total tokens.

The aggregate job also re-scores correctness against the frozen ground truth and uploads:

```text
benchmark-report/report.md
benchmark-report/report.json
```

The Markdown report is also written to the GitHub Actions Step Summary.

## Benchmark isolation

All real-Discourse labs use the same pinned revision:

```text
c89b1a0506a3ec0a249b7f23ac86763b358dc177
```

Condition A has no Rubydex MCP server. Condition B configures Rubydex MCP before Codex starts. Rubydex startup/indexing is therefore part of B's measured Codex process time.

## Cost

The default model is `gpt-5.6-luna`. The aggregator contains an explicit pricing table for its cost estimate. Token counts remain the primary benchmark data; verify current public API pricing before using the cost estimate in a publication.
