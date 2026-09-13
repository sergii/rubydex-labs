#!/usr/bin/env bash
set -euo pipefail

if [ "${RUN_WITH_REAL_OPENAI_API:-false}" != "true" ]; then
  echo "Real OpenAI API execution is disabled." >&2
  echo "Set the repository Actions variable RUN_WITH_REAL_OPENAI_API=true to enable it intentionally." >&2
  exit 78
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not configured in repository Actions secrets." >&2
  exit 1
fi

echo "Real OpenAI API execution is explicitly enabled."
