#!/usr/bin/env python3
"""Aggregate ephemeral GitHub Actions Rubydex benchmark samples."""

from __future__ import annotations

import argparse
from datetime import datetime
from io import BytesIO
import json
from pathlib import Path
import re
import statistics
import zipfile

DISCOURSE_REVISION = "c89b1a0506a3ec0a249b7f23ac86763b358dc177"
LAB04_DECLARATION = "app/services/categories/types/base.rb:5"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.+-]+Z?)")
PATH_LINE_RE = re.compile(r"([A-Za-z0-9_./-]+\.rb:\d+)")

# USD per 1M text tokens. Keep the default benchmark model explicit and
# conservative; unknown models still report tokens but omit cost.
MODEL_PRICING = {
    "gpt-5.6-luna": {"input": 0.20, "cached": 0.02, "output": 1.20},
    "gpt-5-nano": {"input": 0.05, "cached": 0.005, "output": 0.40},
}


def strip_line(line: str) -> str:
    line = line.strip()
    if line.startswith(("- ", "* ")):
        line = line[2:].strip()
    if len(line) >= 2 and line[0] == "`" and line[-1] == "`":
        line = line[1:-1].strip()
    return line


def standalone_path_lines(text: str, declaration: str | None = None) -> set[str]:
    found: set[str] = set()
    for raw in text.splitlines():
        line = strip_line(raw)
        if not line or line.startswith("```"):
            continue
        match = PATH_LINE_RE.fullmatch(line)
        if match:
            found.add(match.group(1))
    if declaration:
        found.discard(declaration)
    return found


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        if raw.startswith("## "):
            current = raw[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(raw)
    return sections


def canonical_named_entries(lines: list[str]) -> set[str]:
    result: set[str] = set()
    for raw in lines:
        line = strip_line(raw)
        if not line or line.startswith("```") or "|" not in line:
            continue
        left, right = [part.strip() for part in line.split("|", 1)]
        path_match = PATH_LINE_RE.fullmatch(right)
        if left and path_match:
            result.add(f"{left} | {path_match.group(1)}")
    return result


def canonical_spec_files(lines: list[str]) -> set[str]:
    result: set[str] = set()
    for raw in lines:
        line = strip_line(raw)
        if line.startswith("```"):
            continue
        if re.fullmatch(r"(?:spec|test)/[A-Za-z0-9_./-]+\.rb", line):
            result.add(line)
    return result


def read_first_entries(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw in lines:
        line = strip_line(raw)
        if not line or line.startswith("```") or "|" not in line:
            continue
        path, reason = [part.strip() for part in line.split("|", 1)]
        if re.fullmatch(r"[A-Za-z0-9_./-]+\.rb", path):
            entries.append((path, reason))
    return entries


def score_set(actual: set[str], expected: set[str]) -> dict:
    tp = actual & expected
    fp = actual - expected
    missed = expected - actual
    precision = len(tp) / len(actual) if actual else 0.0
    recall = len(tp) / len(expected) if expected else 1.0
    return {
        "found": sorted(actual),
        "true_positive": sorted(tp),
        "false_positive": sorted(fp),
        "missed": sorted(missed),
        "precision": precision,
        "recall": recall,
        "exact": not fp and not missed,
    }


def score_lab04(final: str, repo_root: Path) -> dict:
    expected = {
        line.strip()
        for line in (repo_root / "labs/04-real-discourse/ground-truth.txt").read_text().splitlines()
        if line.strip()
    }
    actual = standalone_path_lines(final, LAB04_DECLARATION)
    refs = score_set(actual, expected)
    declaration_correct = LAB04_DECLARATION in final
    return {
        "kind": "constant_references",
        "declaration_correct": declaration_correct,
        "references": refs,
        "exact": declaration_correct and refs["exact"],
    }


def score_lab05(final: str, repo_root: Path) -> dict:
    truth = json.loads((repo_root / "labs/05-real-impact-map/ground-truth.json").read_text())
    sections = split_sections(final)

    descendants = canonical_named_entries(sections.get("Descendants", []))
    production = standalone_path_lines("\n".join(sections.get("Direct production references", [])))
    plugins = canonical_named_entries(sections.get("Plugin extensions", []))
    specs = canonical_spec_files(sections.get("Direct-reference spec files", []))
    read_first = read_first_entries(sections.get("Read-first set", []))

    descendant_score = score_set(descendants, set(truth["named_descendants"]))
    production_score = score_set(production, set(truth["direct_production_references"]))
    plugin_score = score_set(plugins, set(truth["plugin_extensions"]))
    spec_score = score_set(specs, set(truth["direct_reference_spec_files"]))

    declaration_correct = truth["declaration"] in "\n".join(sections.get("Declaration", []))
    structural_exact = (
        declaration_correct
        and descendant_score["exact"]
        and production_score["exact"]
        and plugin_score["exact"]
        and spec_score["exact"]
    )

    rubric = truth["read_first_rubric"]
    selected_paths = {path for path, _ in read_first}
    coverage = {
        category: bool(selected_paths & set(paths))
        for category, paths in rubric["categories"].items()
    }
    read_first_score = {
        "entries": [{"path": path, "reason": reason} for path, reason in read_first],
        "count": len(read_first),
        "max_files": int(rubric["max_files"]),
        "within_limit": len(read_first) <= int(rubric["max_files"]),
        "all_have_reasons": bool(read_first) and all(bool(reason) for _, reason in read_first),
        "coverage": coverage,
        "coverage_count": sum(coverage.values()),
        "coverage_total": len(coverage),
    }

    return {
        "kind": "impact_map",
        "declaration_correct": declaration_correct,
        "descendants": descendant_score,
        "direct_production_references": production_score,
        "plugin_extensions": plugin_score,
        "direct_reference_spec_files": spec_score,
        "structural_exact": structural_exact,
        "read_first": read_first_score,
        "exact": structural_exact,
    }


def decode_log(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"PK"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            parts = []
            for name in archive.namelist():
                if not name.endswith("/"):
                    parts.append(archive.read(name).decode("utf-8", errors="replace"))
            return "\n".join(parts)
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
    candidate = cleaned[start:].strip()
    try:
        value, _ = json.JSONDecoder().raw_decode(candidate)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def parse_codex_log(path: Path) -> dict:
    if not path.exists():
        return {"log_found": False}

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
    uncached = metrics["uncached_input_tokens"]
    cached = metrics["cached_input_tokens"]
    output = metrics["output_tokens"]
    return (
        uncached * pricing["input"]
        + cached * pricing["cached"]
        + output * pricing["output"]
    ) / 1_000_000


def median(samples: list[dict], key: str) -> float | None:
    values = [sample["metrics"].get(key) for sample in samples]
    values = [float(value) for value in values if value is not None]
    return statistics.median(values) if values else None


def pct_delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or a == 0:
        return None
    return (b - a) / a * 100.0


def fmt_number(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "n/a"
    if digits:
        return f"{value:,.{digits}f}"
    return f"{value:,.0f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", choices=["04", "05"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    artifacts_root = Path(args.artifacts)
    logs_root = Path(args.logs)
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    samples: list[dict] = []
    for meta_path in sorted(artifacts_root.glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text())
        final_path = meta_path.parent / "final.txt"
        final = final_path.read_text(errors="replace") if final_path.exists() else ""
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        job_name = f"sample-{condition}-r{repeat}"
        metrics = parse_codex_log(logs_root / f"{job_name}.log")
        metrics["estimated_cost_usd"] = estimated_cost(args.model, metrics)
        score = score_lab04(final, repo_root) if args.lab == "04" else score_lab05(final, repo_root)
        samples.append({
            "job_name": job_name,
            "meta": meta,
            "metrics": metrics,
            "score": score,
            "final": final,
        })

    if not samples:
        raise SystemExit("No sample artifacts were found")

    grouped = {
        condition: [sample for sample in samples if sample["meta"]["condition"] == condition]
        for condition in ("A", "B")
    }

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
    medians = {
        condition: {name: median(grouped[condition], name) for name in metric_names}
        for condition in ("A", "B")
    }

    result = {
        "lab": args.lab,
        "model": args.model,
        "reasoning": args.reasoning,
        "repository": "discourse/discourse",
        "revision": DISCOURSE_REVISION,
        "samples": samples,
        "medians": medians,
        "b_vs_a_percent": {
            name: pct_delta(medians["A"][name], medians["B"][name])
            for name in metric_names
        },
    }

    # Avoid duplicating potentially large final answers in the machine summary.
    json_result = dict(result)
    json_result["samples"] = [
        {key: value for key, value in sample.items() if key != "final"}
        for sample in samples
    ]
    (output_root / "report.json").write_text(json.dumps(json_result, indent=2) + "\n")

    lines = [
        f"# Rubydex benchmark — Lab {args.lab}",
        "",
        f"- Model: `{args.model}`",
        f"- Reasoning: `{args.reasoning}`",
        "- Repository: `discourse/discourse`",
        f"- Revision: `{DISCOURSE_REVISION}`",
        f"- Fresh GitHub-hosted VM per sample: **yes**",
        f"- Samples: A={len(grouped['A'])}, B={len(grouped['B'])}",
        "",
        "## Samples",
        "",
        "| Sample | Correct | Time (s) | Total tokens | Uncached input | Output | Est. cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for sample in sorted(samples, key=lambda item: (item["meta"]["condition"], item["meta"]["repeat"])):
        metrics = sample["metrics"]
        score = sample["score"]
        cost = metrics.get("estimated_cost_usd")
        lines.append(
            "| {name} | {correct} | {time} | {total} | {uncached} | {output} | {cost} |".format(
                name=sample["job_name"],
                correct="yes" if score.get("exact") else "no",
                time=fmt_number(metrics.get("elapsed_seconds"), 1),
                total=fmt_number(metrics.get("total_tokens")),
                uncached=fmt_number(metrics.get("uncached_input_tokens")),
                output=fmt_number(metrics.get("output_tokens")),
                cost="n/a" if cost is None else f"${cost:.4f}",
            )
        )

    lines.extend([
        "",
        "## Median A vs B",
        "",
        "| Metric | A — text | B — Rubydex | B vs A |",
        "| --- | ---: | ---: | ---: |",
    ])

    labels = {
        "elapsed_seconds": "elapsed seconds",
        "total_tokens": "total tokens",
        "input_tokens": "input tokens",
        "cached_input_tokens": "cached input",
        "uncached_input_tokens": "uncached input",
        "output_tokens": "output tokens",
        "reasoning_output_tokens": "reasoning output",
        "estimated_cost_usd": "estimated API cost",
    }
    for name in metric_names:
        a = medians["A"][name]
        b = medians["B"][name]
        delta = result["b_vs_a_percent"][name]
        if name == "estimated_cost_usd":
            a_text = "n/a" if a is None else f"${a:.4f}"
            b_text = "n/a" if b is None else f"${b:.4f}"
        elif name == "elapsed_seconds":
            a_text = fmt_number(a, 1)
            b_text = fmt_number(b, 1)
        else:
            a_text = fmt_number(a)
            b_text = fmt_number(b)
        delta_text = "n/a" if delta is None else f"{delta:+.1f}%"
        lines.append(f"| {labels[name]} | {a_text} | {b_text} | {delta_text} |")

    lines.extend(["", "## Correctness", ""])
    if args.lab == "04":
        for condition in ("A", "B"):
            exact_count = sum(bool(sample["score"]["exact"]) for sample in grouped[condition])
            recalls = [sample["score"]["references"]["recall"] for sample in grouped[condition]]
            median_recall = statistics.median(recalls) if recalls else 0.0
            lines.append(
                f"- **{condition}**: exact {exact_count}/{len(grouped[condition])}; "
                f"median reference recall {median_recall:.1%}."
            )
    else:
        for condition in ("A", "B"):
            exact_count = sum(bool(sample["score"]["structural_exact"]) for sample in grouped[condition])
            coverages = [sample["score"]["read_first"]["coverage_count"] for sample in grouped[condition]]
            coverage_total = (
                grouped[condition][0]["score"]["read_first"]["coverage_total"]
                if grouped[condition]
                else 0
            )
            median_coverage = statistics.median(coverages) if coverages else 0
            lines.append(
                f"- **{condition}**: structural exact {exact_count}/{len(grouped[condition])}; "
                f"median read-first coverage {median_coverage:g}/{coverage_total}."
            )

    missing_usage = [sample["job_name"] for sample in samples if not sample["metrics"].get("usage_found")]
    if missing_usage:
        lines.extend([
            "",
            "> **Instrumentation warning:** token usage was not recovered from job logs for: "
            + ", ".join(missing_usage),
        ])

    lines.extend([
        "",
        "## Notes",
        "",
        "- Every sample runs on a separate GitHub-hosted runner VM; A cannot warm B's filesystem or Rubydex index.",
        "- Rubydex MCP startup/indexing happens inside the Codex process and therefore remains in measured agent time.",
        "- Cost is an estimate from reported token usage and the hard-coded price table in the aggregator; verify current model pricing before publication.",
        "- Full final answers and per-sample metadata are retained in the sample artifacts for manual review.",
        "",
    ])

    (output_root / "report.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
