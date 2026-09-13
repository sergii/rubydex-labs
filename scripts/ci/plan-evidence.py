#!/usr/bin/env python3
"""Generate a Lab 11 EvidencePlan from one natural-language request.

Defense in depth: this script refuses to make a real OpenAI API call unless
RUN_WITH_REAL_OPENAI_API=true is present in the process environment.
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
BACKENDS = ["source", "rubydex", "runtime_observability", "architecture_knowledge"]


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


def planner_schema() -> dict:
    step = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "evidence_class": {"type": "string", "enum": CLASSES},
            "backend": {"type": "string", "enum": BACKENDS},
            "requirement": {"type": "string", "enum": ["required", "optional"]},
            "purpose": {"type": "string", "minLength": 1},
            "depends_on": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "uniqueItems": True,
            },
            "query_hint": {"type": ["string", "null"]},
            "freshness": {"type": ["string", "null"]},
        },
        "required": [
            "id",
            "evidence_class",
            "backend",
            "requirement",
            "purpose",
            "depends_on",
            "query_hint",
            "freshness",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "strategy": {
                "type": "string",
                "enum": ["parallel_when_possible", "sequential"],
            },
            "steps": {"type": "array", "minItems": 1, "maxItems": 4, "items": step},
        },
        "required": ["strategy", "steps"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-file", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", default="low", choices=["none", "low", "medium", "high"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if os.environ.get("RUN_WITH_REAL_OPENAI_API", "").strip().lower() != "true":
        raise SystemExit(
            "Refusing real OpenAI API call: set RUN_WITH_REAL_OPENAI_API=true explicitly."
        )

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    policy = (ROOT / "labs/11-evidence-planner/planner-policy.md").read_text()
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
                "name": "evidence_plan",
                "strict": True,
                "schema": planner_schema(),
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

    model_plan = json.loads(extract_output_text(response))
    plan = {
        "schema_version": "1",
        "request": request_text,
        "strategy": model_plan["strategy"],
        "steps": model_plan["steps"],
    }

    result = {
        "mode": "planner",
        "model": args.model,
        "reasoning": args.reasoning,
        "response_id": response.get("id"),
        "elapsed_seconds": elapsed,
        "usage": normalize_usage(response),
        "plan": plan,
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(plan, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
