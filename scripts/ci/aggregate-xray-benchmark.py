#!/usr/bin/env python3
"""Aggregate Lab 06 X-Ray benchmark samples."""

from __future__ import annotations

import argparse
from datetime import datetime
from io import BytesIO
import json
from pathlib import Path
import re
import statistics
import zipfile

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.+-]+Z?)")
MODEL_PRICING = {
    "gpt-5.6-luna": {"input": 0.20, "cached": 0.02, "output": 1.20},
    "gpt-5-nano": {"input": 0.05, "cached": 0.005, "output": 0.40},
}
CONDITIONS = ("A", "B", "C", "D")
CONDITION_LABELS = {
    "A": "text",
    "B": "Rubydex",
    "C": "Rubydex + knowledge",
    "D": "knowledge only",
}


def strip_line(line: str) -> str:
    line = line.strip()
    if line.startswith(("- ", "* ")):
        line = line[2:].strip()
    if len(line) >= 2 and line[0] == "`" and line[-1] == "`":
        line = line[1:-1].strip()
    return line


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        if raw.startswith("## "):
            current = raw[3:].strip()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(raw)
    return sections


def canonical_ids(lines: list[str], prefix: str) -> set[str]:
    pattern = re.compile(rf"({re.escape(prefix)}[A-Z0-9-]+)")
    result: set[str] = set()
    for raw in lines:
        line = strip_line(raw)
        if not line or line == "NONE" or line.startswith("```"):
            continue
        match = pattern.match(line)
        if match:
            result.add(match.group(1))
    return result


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


def score_final(final: str, truth: dict) -> dict:
    sections = split_sections(final)
    impacts = score_set(canonical_ids(sections.get("Impacts", []), "IMPACT-"), set(truth["impacts"]))
    risks = score_set(canonical_ids(sections.get("Risks", []), "RISK-"), set(truth["risks"]))
    verification = score_set(canonical_ids(sections.get("Verification", []), "VERIFY-"), set(truth["verification"]))
    policies = score_set(canonical_ids(sections.get("Policy violations", []), "POLICY-"), set(truth["policy_violations"]))
    recommendation_text = "\n".join(sections.get("Recommendation", []))
    recommendation = next((value for value in ("SAFE", "CAUTION", "BLOCK") if re.search(rf"\b{value}\b", recommendation_text)), None)
    consequence_exact = impacts["exact"] and risks["exact"] and verification["exact"]
    knowledge_exact = policies["exact"] and recommendation == truth["recommendation"]
    return {
        "impacts": impacts,
        "risks": risks,
        "verification": verification,
        "policy_violations": policies,
        "recommendation": recommendation,
        "recommendation_correct": recommendation == truth["recommendation"],
        "consequence_exact": consequence_exact,
        "knowledge_exact": knowledge_exact,
        "exact": consequence_exact and knowledge_exact,
    }


def decode_log(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"PK"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return "\n".join(archive.read(name).decode("utf-8", errors="replace") for name in archive.namelist() if not name.endswith("/"))
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
    process_start = first_event = completed_at = None
    usage: dict = {}
    for line in decode_log(path).splitlines():
        timestamp = parse_timestamp(line)
        if process_start is None and "Running:" in line and " exec " in line:
            process_start = timestamp
        event = parse_json_event(line)
        if not event:
            continue
        if first_event is None:
            first_event = timestamp
        if event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
            completed_at = timestamp
    input_tokens = int(usage.get("input_tokens") or 0)
    cached_input_tokens = int(usage.get("cached_input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    reasoning_output_tokens = int(usage.get("reasoning_output_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or (input_tokens + output_tokens))
    started_at = process_start or first_event
    elapsed_seconds = max((completed_at - started_at).total_seconds(), 0.0) if started_at and completed_at else None
    return {
        "log_found": True,
        "usage_found": bool(usage),
        "elapsed_seconds": elapsed_seconds,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": max(input_tokens - cached_input_tokens, 0),
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


def median_metric(samples: list[dict], key: str) -> float | None:
    values = [sample["metrics"].get(key) for sample in samples]
    values = [float(value) for value in values if value is not None]
    return statistics.median(values) if values else None


def median_score(samples: list[dict], section: str, metric: str) -> float:
    values = [float(sample["score"][section][metric]) for sample in samples]
    return statistics.median(values) if values else 0.0


def pct_delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or a == 0:
        return None
    return (b - a) / a * 100.0


def fmt(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    truth = json.loads((repo_root / "labs/06-xray-impact/ground-truth.json").read_text())
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    samples: list[dict] = []
    for meta_path in sorted(Path(args.artifacts).glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text())
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        job_name = f"sample-{condition}-r{repeat}"
        final_path = meta_path.parent / "final.txt"
        final = final_path.read_text(errors="replace") if final_path.exists() else ""
        metrics = parse_codex_log(Path(args.logs) / f"{job_name}.log")
        metrics["estimated_cost_usd"] = estimated_cost(args.model, metrics)
        samples.append({"job_name": job_name, "meta": meta, "metrics": metrics, "score": score_final(final, truth)})

    if not samples:
        raise SystemExit("No sample artifacts were found")

    grouped = {condition: [s for s in samples if s["meta"]["condition"] == condition] for condition in CONDITIONS}
    metric_names = ["elapsed_seconds", "total_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens", "estimated_cost_usd"]
    medians = {condition: {name: median_metric(grouped[condition], name) for name in metric_names} for condition in CONDITIONS}

    result = {
        "lab": "06",
        "model": args.model,
        "reasoning": args.reasoning,
        "conditions": list(CONDITIONS),
        "samples": samples,
        "medians": medians,
        "deltas": {
            "b_vs_a": {name: pct_delta(medians["A"][name], medians["B"][name]) for name in metric_names},
            "c_vs_b": {name: pct_delta(medians["B"][name], medians["C"][name]) for name in metric_names},
            "d_vs_a": {name: pct_delta(medians["A"][name], medians["D"][name]) for name in metric_names},
            "c_vs_d": {name: pct_delta(medians["D"][name], medians["C"][name]) for name in metric_names},
        },
    }
    (output_root / "report.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Rubydex benchmark - Lab 06 X-Ray",
        "",
        f"- Model: `{args.model}`",
        f"- Reasoning: `{args.reasoning}`",
        "- Fixture: `labs/06-xray-impact/fixture`",
        "- Fresh GitHub-hosted VM per sample: **yes**",
        "- Samples: " + ", ".join(f"{c}={len(grouped[c])}" for c in CONDITIONS),
        "",
        "## Samples",
        "",
        "| Sample | Consequence exact | Knowledge exact | Time (s) | Total tokens |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for sample in sorted(samples, key=lambda item: (item["meta"]["condition"], item["meta"]["repeat"])):
        lines.append(
            f"| {sample['job_name']} | {'yes' if sample['score']['consequence_exact'] else 'no'} | "
            f"{'yes' if sample['score']['knowledge_exact'] else 'no'} | {fmt(sample['metrics'].get('elapsed_seconds'), 1)} | "
            f"{fmt(sample['metrics'].get('total_tokens'))} |"
        )

    lines += [
        "",
        "## Median correctness",
        "",
        "| Condition | Impact recall | Impact precision | Risk recall | Risk precision | Verification recall | Policy recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in CONDITIONS:
        items = grouped[condition]
        lines.append(
            f"| {condition} | {median_score(items, 'impacts', 'recall'):.1%} | {median_score(items, 'impacts', 'precision'):.1%} | "
            f"{median_score(items, 'risks', 'recall'):.1%} | {median_score(items, 'risks', 'precision'):.1%} | "
            f"{median_score(items, 'verification', 'recall'):.1%} | {median_score(items, 'policy_violations', 'recall'):.1%} |"
        )

    header = "| Metric | " + " | ".join(f"{c} - {CONDITION_LABELS[c]}" for c in CONDITIONS) + " |"
    separator = "| --- | " + " | ".join("---:" for _ in CONDITIONS) + " |"
    lines += ["", "## Median cost / latency", "", header, separator]
    labels = {
        "elapsed_seconds": "elapsed seconds",
        "total_tokens": "total tokens",
        "uncached_input_tokens": "uncached input",
        "output_tokens": "output tokens",
        "reasoning_output_tokens": "reasoning output",
        "estimated_cost_usd": "estimated API cost",
    }
    for name in metric_names:
        values = []
        for condition in CONDITIONS:
            value = medians[condition][name]
            if name == "estimated_cost_usd":
                values.append("n/a" if value is None else f"${value:.4f}")
            elif name == "elapsed_seconds":
                values.append(fmt(value, 1))
            else:
                values.append(fmt(value))
        lines.append(f"| {labels[name]} | " + " | ".join(values) + " |")

    lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- Impact/risk/verification use the same closed candidate vocabulary in all four conditions.",
        "- Policy IDs are not exposed to A/B. C and D receive the same explicit company architecture knowledge and targeted skill.",
        "- C has Rubydex + knowledge; D has the same knowledge without Rubydex, isolating the knowledge contribution.",
        "- `consequence_exact` intentionally excludes policy/recommendation.",
        "- Rubydex MCP startup/indexing is included in B/C measured agent time.",
        "- Token/cost differences should be interpreted from repeated samples, not a single run.",
        "",
    ]
    (output_root / "report.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
