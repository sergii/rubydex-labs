#!/usr/bin/env python3
"""Aggregate Lab 08 autonomous semantic-escalation benchmark."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = ROOT / "scripts/ci/aggregate-task-shape.py"
spec = importlib.util.spec_from_file_location("task_shape_aggregate", HELPER_PATH)
helper = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(helper)

CONDITIONS = ("D", "E", "F")
FIELDS = (
    "named_descendants",
    "direct_production_references",
    "plugin_extensions",
    "direct_reference_spec_files",
)
SEARCH_RE = re.compile(r"(^|[;&|()\s])(rg|grep|find)(\s|$)")
READ_RE = re.compile(r"(^|[;&|()\s])(sed|cat|head|tail|awk)(\s|$)")
RUBY_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])((?:app|plugins|spec|lib)/[A-Za-z0-9_./-]+\.rb)(?=[:\s'\"`]|$)")


def median(values):
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def fmt_num(value, digits=0):
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def fmt_pct(value):
    return "n/a" if value is None else f"{value * 100:.1f}%"


def fmt_cost(value):
    return "n/a" if value is None else f"${value:.4f}"


def parse_navigation(log_path: Path) -> dict:
    if not log_path.exists():
        return {
            "command_count": None,
            "search_command_count": None,
            "read_command_count": None,
            "ruby_files_read_approx": None,
            "rubydex_tool_calls": None,
            "rubydex_tools": [],
        }

    text = helper.decode_log(log_path)
    command_ids = set()
    search_ids = set()
    read_ids = set()
    ruby_files = set()
    rubydex_ids = set()
    rubydex_tools = set()

    for line in text.splitlines():
        event = helper.parse_json_event(line)
        if not event:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or "")
        item_type = str(item.get("type") or "")

        if item_type == "command_execution" and event.get("type") == "item.completed":
            command = str(item.get("command") or "")
            output = str(item.get("aggregated_output") or "")
            key = item_id or f"cmd-{len(command_ids)}"
            command_ids.add(key)
            if SEARCH_RE.search(command):
                search_ids.add(key)
            if READ_RE.search(command):
                read_ids.add(key)
                ruby_files.update(RUBY_PATH_RE.findall(command))
                ruby_files.update(RUBY_PATH_RE.findall(output))

        serialized = json.dumps(item, sort_keys=True).lower()
        if "rubydex" in serialized and ("mcp" in item_type.lower() or "tool" in item_type.lower()):
            key = item_id or f"rdx-{len(rubydex_ids)}"
            rubydex_ids.add(key)
            for field in ("tool", "tool_name", "name"):
                value = item.get(field)
                if isinstance(value, str) and value:
                    rubydex_tools.add(value)
            if isinstance(item.get("server"), str) and isinstance(item.get("tool"), str):
                rubydex_tools.add(f"{item['server']}.{item['tool']}")

    return {
        "command_count": len(command_ids),
        "search_command_count": len(search_ids),
        "read_command_count": len(read_ids),
        "ruby_files_read_approx": len(ruby_files),
        "rubydex_tool_calls": len(rubydex_ids),
        "rubydex_tools": sorted(rubydex_tools),
        "ruby_files_read": sorted(ruby_files),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    truth = json.loads((ROOT / "labs/07-task-shape-boundary/ground-truth.json").read_text())
    artifacts_root = Path(args.artifacts)
    logs_root = Path(args.logs)
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    samples = []
    for meta_path in sorted(artifacts_root.glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text())
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        job_name = f"sample-{condition}-r{repeat}"
        final_path = meta_path.parent / "final.txt"
        final = final_path.read_text(errors="replace") if final_path.exists() else ""
        log_path = logs_root / f"{job_name}.log"
        metrics = helper.parse_codex_log(log_path)
        metrics["estimated_cost_usd"] = helper.estimated_cost(args.model, metrics)
        metrics.update(parse_navigation(log_path))
        score = helper.score_sample("impact", final, truth)
        samples.append({
            "job_name": job_name,
            "meta": meta,
            "metrics": metrics,
            "score": score,
        })

    if not samples:
        raise SystemExit("No sample artifacts found")

    summary = {}
    metric_names = (
        "elapsed_seconds",
        "total_tokens",
        "uncached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "estimated_cost_usd",
        "command_count",
        "search_command_count",
        "read_command_count",
        "ruby_files_read_approx",
        "rubydex_tool_calls",
    )

    for condition in CONDITIONS:
        group = [s for s in samples if s["meta"]["condition"] == condition]
        item = {
            "count": len(group),
            "exact_count": sum(1 for s in group if s["score"].get("exact")),
            "medians": {name: median([s["metrics"].get(name) for s in group]) for name in metric_names},
            "field_median_precision": {},
            "field_median_recall": {},
            "rubydex_tools": sorted({
                tool for s in group for tool in s["metrics"].get("rubydex_tools", [])
            }),
        }
        for field in FIELDS:
            item["field_median_precision"][field] = median([
                s["score"].get(field, {}).get("precision") for s in group
            ])
            item["field_median_recall"][field] = median([
                s["score"].get(field, {}).get("recall") for s in group
            ])
        coverage = [s["score"].get("read_first", {}).get("coverage_count") for s in group]
        item["median_read_first_coverage"] = median(coverage)
        item["read_first_coverage_total"] = len(truth["read_first_rubric"]["categories"])
        summary[condition] = item

    result = {
        "lab": "08",
        "model": args.model,
        "reasoning": args.reasoning,
        "repository": truth["repository"],
        "revision": truth["revision"],
        "target": truth["target"],
        "samples": samples,
        "summary": summary,
    }
    (output_root / "report.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Lab 08 — autonomous semantic escalation",
        "",
        f"- Model: `{args.model}`",
        f"- Reasoning: `{args.reasoning}`",
        f"- Repository: `{truth['repository']}`",
        f"- Revision: `{truth['revision']}`",
        f"- Target: `{truth['target']}`",
        "",
        "## Correctness and navigation economics",
        "",
        "| Condition | Exact | Desc recall | Ref recall | Plugin recall | Spec recall | Read-first | RDX calls | Shell cmds | Search cmds | Ruby files read* | Sec | Total tokens | Uncached | Cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for condition in CONDITIONS:
        s = summary[condition]
        m = s["medians"]
        r = s["field_median_recall"]
        lines.append(
            f"| {condition} | {s['exact_count']}/{s['count']} | "
            f"{fmt_pct(r['named_descendants'])} | {fmt_pct(r['direct_production_references'])} | "
            f"{fmt_pct(r['plugin_extensions'])} | {fmt_pct(r['direct_reference_spec_files'])} | "
            f"{fmt_num(s['median_read_first_coverage'])}/{s['read_first_coverage_total']} | "
            f"{fmt_num(m['rubydex_tool_calls'])} | {fmt_num(m['command_count'])} | "
            f"{fmt_num(m['search_command_count'])} | {fmt_num(m['ruby_files_read_approx'])} | "
            f"{fmt_num(m['elapsed_seconds'], 1)} | {fmt_num(m['total_tokens'])} | "
            f"{fmt_num(m['uncached_input_tokens'])} | {fmt_cost(m['estimated_cost_usd'])} |"
        )

    lines += [
        "",
        "\* `Ruby files read` is an approximation from completed shell commands that printed file contents; it intentionally excludes paths merely returned by search output.",
        "",
        "## Rubydex tools observed",
        "",
    ]
    for condition in CONDITIONS:
        tools = summary[condition]["rubydex_tools"]
        lines.append(f"- **{condition}:** {', '.join(f'`{tool}`' for tool in tools) if tools else 'none'}")

    lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- D and E receive identical prompts; E differs only by optional Rubydex MCP availability.",
        "- F receives the same task plus a minimal semantic-escalation decision rule; Rubydex remains optional.",
        "- The frozen structural ground truth is reused unchanged from Lab 07 and is not exposed to the agent workspace.",
        "- Tool-selection claims require actual Rubydex calls in logs. Correctness differences without tool calls must not be attributed to Rubydex.",
        "- Three samples expose stochastic behavior but are not a publication-grade statistical estimate.",
    ]

    report = "\n".join(lines) + "\n"
    (output_root / "report.md").write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
