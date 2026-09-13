#!/usr/bin/env python3
"""Aggregate the Lab 07 task-shape boundary benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime
from io import BytesIO
import json
from pathlib import Path
import re
import statistics
import zipfile

SCENARIOS = ["declaration", "descendants", "references", "neighborhood", "impact"]
DISCOURSE_REVISION = "c89b1a0506a3ec0a249b7f23ac86763b358dc177"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.+-]+Z?)")

# USD per 1M text tokens. These are benchmark assumptions, not a live
# pricing lookup. Unknown models still report token metrics but omit cost.
MODEL_PRICING = {
    "gpt-5.6-luna": {"input": 0.20, "cached": 0.02, "output": 1.20},
    "gpt-5-nano": {"input": 0.05, "cached": 0.005, "output": 0.40},
}


def decode_log(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"PK"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return "\n".join(
                archive.read(name).decode("utf-8", errors="replace")
                for name in archive.namelist()
                if not name.endswith("/")
            )
    return data.decode("utf-8", errors="replace")


def parse_timestamp(line: str) -> datetime | None:
    match = TIMESTAMP_RE.match(line)
    if not match:
        return None
    value = match.group(1)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_json_event(line: str) -> dict | None:
    cleaned = ANSI_RE.sub("", line)
    start = cleaned.find("{")
    if start < 0:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(cleaned[start:].strip())
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def parse_codex_log(path: Path) -> dict:
    if not path.exists():
        return {"log_found": False, "usage_found": False}

    text = decode_log(path)
    process_start: datetime | None = None
    first_event: datetime | None = None
    completed_at: datetime | None = None
    usage: dict = {}
    thread_id: str | None = None

    for line in text.splitlines():
        timestamp = parse_timestamp(line)
        if process_start is None and "Running:" in line and " exec " in line:
            process_start = timestamp

        event = parse_json_event(line)
        if not event:
            continue
        if first_event is None:
            first_event = timestamp
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id") or event.get("thread", {}).get("id")
        elif event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
            completed_at = timestamp

    input_tokens = int(usage.get("input_tokens") or 0)
    cached_input_tokens = int(usage.get("cached_input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    reasoning_output_tokens = int(usage.get("reasoning_output_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or (input_tokens + output_tokens))
    uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)

    started_at = process_start or first_event
    elapsed_seconds = None
    if started_at is not None and completed_at is not None:
        elapsed_seconds = max((completed_at - started_at).total_seconds(), 0.0)

    return {
        "log_found": True,
        "thread_id": thread_id,
        "elapsed_seconds": elapsed_seconds,
        "usage_found": bool(usage),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": uncached_input_tokens,
        "output_tokens": output_tokens,
        "reasoning_output_tokens": reasoning_output_tokens,
        "total_tokens": total_tokens,
    }


def estimated_cost(model: str, metrics: dict) -> float | None:
    pricing = MODEL_PRICING.get(model)
    if not pricing or not metrics.get("usage_found"):
        return None
    return (
        metrics["uncached_input_tokens"] * pricing["input"]
        + metrics["cached_input_tokens"] * pricing["cached"]
        + metrics["output_tokens"] * pricing["output"]
    ) / 1_000_000


def extract_payload(text: str) -> tuple[dict | None, str | None]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    if start < 0:
        return None, "no JSON object found"
    try:
        payload, _ = json.JSONDecoder().raw_decode(stripped[start:])
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "top-level JSON value is not an object"
    return payload, None


def as_string_set(value) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def score_set(actual: set[str], expected: set[str]) -> dict:
    tp = actual & expected
    fp = actual - expected
    missed = expected - actual
    return {
        "found": sorted(actual),
        "true_positive": sorted(tp),
        "false_positive": sorted(fp),
        "missed": sorted(missed),
        "precision": len(tp) / len(actual) if actual else 0.0,
        "recall": len(tp) / len(expected) if expected else 1.0,
        "exact": not fp and not missed,
    }


def score_sample(scenario: str, final: str, truth: dict) -> dict:
    payload, parse_error = extract_payload(final)
    if payload is None:
        return {"parse_error": parse_error, "exact": False}

    result: dict = {"parse_error": None}
    declaration = payload.get("declaration")
    declaration_correct = declaration == truth["declaration"]

    descendants = score_set(
        as_string_set(payload.get("named_descendants")),
        set(truth["named_descendants"]),
    )
    references = score_set(
        as_string_set(payload.get("direct_production_references")),
        set(truth["direct_production_references"]),
    )
    plugins = score_set(
        as_string_set(payload.get("plugin_extensions")),
        set(truth["plugin_extensions"]),
    )
    specs = score_set(
        as_string_set(payload.get("direct_reference_spec_files")),
        set(truth["direct_reference_spec_files"]),
    )

    result["declaration_correct"] = declaration_correct
    if scenario == "declaration":
        result["exact"] = declaration_correct
        return result

    if scenario == "descendants":
        result["named_descendants"] = descendants
        result["exact"] = descendants["exact"]
        return result

    if scenario == "references":
        result["direct_production_references"] = references
        result["exact"] = references["exact"]
        return result

    result["named_descendants"] = descendants
    result["direct_production_references"] = references

    if scenario == "neighborhood":
        result["exact"] = declaration_correct and descendants["exact"] and references["exact"]
        return result

    if scenario != "impact":
        raise ValueError(f"unknown scenario: {scenario}")

    result["plugin_extensions"] = plugins
    result["direct_reference_spec_files"] = specs

    raw_read_first = payload.get("read_first")
    entries = []
    if isinstance(raw_read_first, list):
        for item in raw_read_first:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            reason = item.get("reason")
            if isinstance(path, str) and path.strip():
                entries.append({
                    "path": path.strip(),
                    "reason": reason.strip() if isinstance(reason, str) else "",
                })

    rubric = truth["read_first_rubric"]
    selected_paths = {entry["path"] for entry in entries}
    coverage = {
        category: bool(selected_paths & set(paths))
        for category, paths in rubric["categories"].items()
    }
    result["read_first"] = {
        "entries": entries,
        "count": len(entries),
        "max_files": int(rubric["max_files"]),
        "within_limit": len(entries) <= int(rubric["max_files"]),
        "all_have_reasons": bool(entries) and all(bool(entry["reason"]) for entry in entries),
        "coverage": coverage,
        "coverage_count": sum(coverage.values()),
        "coverage_total": len(coverage),
    }
    result["exact"] = (
        declaration_correct
        and descendants["exact"]
        and references["exact"]
        and plugins["exact"]
        and specs["exact"]
    )
    return result


def median(samples: list[dict], key: str) -> float | None:
    values = [sample["metrics"].get(key) for sample in samples]
    values = [float(value) for value in values if value is not None]
    return statistics.median(values) if values else None


def pct_delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or a == 0:
        return None
    return (b - a) / a * 100.0


def fmt_num(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.1f}%"


def fmt_cost(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.4f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    truth = json.loads((repo_root / "labs/07-task-shape-boundary/ground-truth.json").read_text())
    artifacts_root = Path(args.artifacts)
    logs_root = Path(args.logs)
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    samples: list[dict] = []
    for meta_path in sorted(artifacts_root.glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text())
        scenario = meta["scenario"]
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        job_name = f"sample-{scenario}-{condition}-r{repeat}"
        final_path = meta_path.parent / "final.txt"
        final = final_path.read_text(errors="replace") if final_path.exists() else ""
        metrics = parse_codex_log(logs_root / f"{job_name}.log")
        metrics["estimated_cost_usd"] = estimated_cost(args.model, metrics)
        score = score_sample(scenario, final, truth)
        samples.append({
            "job_name": job_name,
            "meta": meta,
            "metrics": metrics,
            "score": score,
            "final": final,
        })

    if not samples:
        raise SystemExit("No sample artifacts were found")

    metric_names = [
        "elapsed_seconds",
        "total_tokens",
        "input_tokens",
        "cached_input_tokens",
        "uncached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "estimated_cost_usd",
    ]

    summary: dict = {}
    for scenario in SCENARIOS:
        summary[scenario] = {}
        for condition in ("A", "B"):
            group = [
                sample for sample in samples
                if sample["meta"]["scenario"] == scenario
                and sample["meta"]["condition"] == condition
            ]
            medians = {name: median(group, name) for name in metric_names}
            exact_count = sum(1 for sample in group if sample["score"].get("exact"))
            item = {
                "count": len(group),
                "exact_count": exact_count,
                "medians": medians,
            }
            if scenario == "impact" and group:
                coverage_values = [
                    sample["score"].get("read_first", {}).get("coverage_count")
                    for sample in group
                ]
                coverage_values = [value for value in coverage_values if value is not None]
                item["median_read_first_coverage"] = (
                    statistics.median(coverage_values) if coverage_values else None
                )
                item["read_first_coverage_total"] = len(truth["read_first_rubric"]["categories"])
            summary[scenario][condition] = item

        summary[scenario]["b_vs_a_percent"] = {
            name: pct_delta(
                summary[scenario]["A"]["medians"][name],
                summary[scenario]["B"]["medians"][name],
            )
            for name in metric_names
        }

    json_samples = [
        {key: value for key, value in sample.items() if key != "final"}
        for sample in samples
    ]
    result = {
        "lab": "07",
        "model": args.model,
        "reasoning": args.reasoning,
        "repository": truth["repository"],
        "revision": truth["revision"],
        "target": truth["target"],
        "scenarios": SCENARIOS,
        "samples": json_samples,
        "summary": summary,
    }
    (output_root / "report.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Rubydex benchmark — Lab 07 task-shape boundary",
        "",
        f"- Model: `{args.model}`",
        f"- Reasoning: `{args.reasoning}`",
        f"- Repository: `{truth['repository']}`",
        f"- Revision: `{truth['revision']}`",
        f"- Target: `{truth['target']}`",
        "- Fresh GitHub-hosted VM per sample: **yes**",
        "",
        "## Crossover table",
        "",
        "| Scenario | Exact A | Exact B | A sec | B sec | Δ time | A uncached | B uncached | Δ uncached | A total | B total | Δ total | A cost | B cost | Δ cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for scenario in SCENARIOS:
        a = summary[scenario]["A"]
        b = summary[scenario]["B"]
        delta = summary[scenario]["b_vs_a_percent"]
        lines.append(
            "| " + " | ".join([
                scenario,
                f"{a['exact_count']}/{a['count']}",
                f"{b['exact_count']}/{b['count']}",
                fmt_num(a["medians"]["elapsed_seconds"], 1),
                fmt_num(b["medians"]["elapsed_seconds"], 1),
                fmt_pct(delta["elapsed_seconds"]),
                fmt_num(a["medians"]["uncached_input_tokens"]),
                fmt_num(b["medians"]["uncached_input_tokens"]),
                fmt_pct(delta["uncached_input_tokens"]),
                fmt_num(a["medians"]["total_tokens"]),
                fmt_num(b["medians"]["total_tokens"]),
                fmt_pct(delta["total_tokens"]),
                fmt_cost(a["medians"]["estimated_cost_usd"]),
                fmt_cost(b["medians"]["estimated_cost_usd"]),
                fmt_pct(delta["estimated_cost_usd"]),
            ]) + " |"
        )

    lines += [
        "",
        "## Token decomposition",
        "",
        "| Scenario | A input | B input | Δ input | A cached | B cached | Δ cached | A output | B output | Δ output | A reasoning | B reasoning | Δ reasoning |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario in SCENARIOS:
        a = summary[scenario]["A"]["medians"]
        b = summary[scenario]["B"]["medians"]
        delta = summary[scenario]["b_vs_a_percent"]
        lines.append(
            "| " + " | ".join([
                scenario,
                fmt_num(a["input_tokens"]),
                fmt_num(b["input_tokens"]),
                fmt_pct(delta["input_tokens"]),
                fmt_num(a["cached_input_tokens"]),
                fmt_num(b["cached_input_tokens"]),
                fmt_pct(delta["cached_input_tokens"]),
                fmt_num(a["output_tokens"]),
                fmt_num(b["output_tokens"]),
                fmt_pct(delta["output_tokens"]),
                fmt_num(a["reasoning_output_tokens"]),
                fmt_num(b["reasoning_output_tokens"]),
                fmt_pct(delta["reasoning_output_tokens"]),
            ]) + " |"
        )

    impact_a = summary["impact"]["A"]
    impact_b = summary["impact"]["B"]
    lines += [
        "",
        "## Impact read-first coverage",
        "",
        f"- A median coverage: {fmt_num(impact_a.get('median_read_first_coverage'))}/{impact_a.get('read_first_coverage_total', 'n/a')}",
        f"- B median coverage: {fmt_num(impact_b.get('median_read_first_coverage'))}/{impact_b.get('read_first_coverage_total', 'n/a')}",
        "",
        "## Notes",
        "",
        "- Scenario breadth increases while repository, revision, target, model, and runner isolation remain fixed.",
        "- Condition B includes Rubydex MCP startup/indexing inside the measured Codex session.",
        "- Exactness is deterministic set equality against the frozen ground truth; `impact` read-first coverage is reported separately.",
        "- Cost is an estimate from the harness price table, not a live pricing lookup.",
        "- Full final answers and per-sample scores remain in the report JSON and source sample artifacts.",
    ]

    report_md = "\n".join(lines) + "\n"
    (output_root / "report.md").write_text(report_md)
    print(report_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
