#!/usr/bin/env python3
"""Classify a natural-language engineering request into an evidence class.

Uses the OpenAI Responses API with Structured Outputs. The expected benchmark
label is intentionally never passed to this process.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
CLASSES = [
    "SOURCE_LOCAL",
    "SEMANTIC_RELATIONSHIP_SET",
    "RUNTIME_BEHAVIOR",
    "ARCHITECTURE_KNOWLEDGE",
]


def extract_output_text(response: dict) -> str:
    value = response.get("output_text")
    if isinstance(value, str) and value.strip():
        return value
    for item in response.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                return content["text"]
    raise ValueError("Responses API payload did not contain output text")


def normalize_usage(response: dict) -> dict:
    usage = response.get("usage") or {}
    input_details = usage.get("input_tokens_details") or {}
    output_details = usage.get("output_tokens_details") or {}
    input_tokens = int(usage.get("input_tokens") or 0)
    cached = int(input_details.get("cached_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (input_tokens + output_tokens))
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "uncached_input_tokens": max(input_tokens - cached, 0),
        "output_tokens": output_tokens,
        "reasoning_output_tokens": int(output_details.get("reasoning_tokens") or 0),
        "total_tokens": total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-file", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", default="low", choices=["none", "low", "medium", "high"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    policy = (ROOT / "labs/10-natural-language-evidence-routing/classifier-policy.md").read_text()
    request_text = Path(args.request_file).read_text().strip()

    body = {
        "model": args.model,
        "store": False,
        "reasoning": {"effort": args.reasoning},
        "instructions": policy,
        "input": request_text,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "evidence_route",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "evidence_class": {"type": "string", "enum": CLASSES},
                        "rationale": {"type": "string", "minLength": 1},
                    },
                    "required": ["evidence_class", "rationale"],
                    "additionalProperties": False,
                },
            }
        },
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as handle:
            response = json.loads(handle.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI Responses API returned HTTP {exc.code}: {payload}") from exc
    elapsed = time.monotonic() - started

    parsed = json.loads(extract_output_text(response))
    evidence_class = parsed.get("evidence_class")
    if evidence_class not in CLASSES:
        raise SystemExit(f"Unexpected evidence class: {evidence_class!r}")

    result = {
        "mode": "classifier",
        "model": args.model,
        "reasoning": args.reasoning,
        "response_id": response.get("id"),
        "predicted_class": evidence_class,
        "rationale": parsed.get("rationale", ""),
        "elapsed_seconds": elapsed,
        "usage": normalize_usage(response),
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(evidence_class)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
