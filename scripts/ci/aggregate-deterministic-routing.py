#!/usr/bin/env python3
"""Aggregate Lab 09 task-shape routing benchmark."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


helper = load_module("task_shape_aggregate", ROOT / "scripts/ci/aggregate-task-shape.py")
nav = load_module("autonomous_aggregate", ROOT / "scripts/ci/aggregate-autonomous-escalation.py")
router = load_module("task_shape_router", ROOT / "scripts/ci/task-shape-router.py")

CONDITIONS = ("E", "F", "G")
SCENARIOS = tuple(helper.SCENARIOS)


def median(values):
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def fmt_num(value, digits=0):
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def fmt_cost(value):
    return "n/a" if value is None else f"${value:.4f}"


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
        scenario = meta["scenario"]
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        job_name = f"sample-{scenario}-{condition}-r{repeat}"
        final_path = meta_path.parent / "final.txt"
        final = final_path.read_text(errors="replace") if final_path.exists() else ""
        log_path = logs_root / f"{job_name}.log"
        metrics = helper.parse_codex_log(log_path)
        metrics["estimated_cost_usd"] = helper.estimated_cost(args.model, metrics)
        metrics.update(nav.parse_navigation(log_path))
        score = helper.score_sample(scenario, final, truth)
        observed_semantic = (metrics.get("rubydex_tool_calls") or 0) > 0
        expected_semantic = router.route(scenario) == "semantic"
        samples.append({
            "job_name": job_name,
            "meta": meta,
            "metrics": metrics,
            "score": score,
            "routing": {
                "expected_semantic": expected_semantic,
                "observed_semantic": observed_semantic,
                "selection_correct": expected_semantic == observed_semantic,
            },
        })

    if not samples:
        raise SystemExit("No sample artifacts found")

    summary = {}
    for scenario in SCENARIOS:
        summary[scenario] = {}
        for condition in CONDITIONS:
            group = [s for s in samples if s["meta"]["scenario"] == scenario and s["meta"]["condition"] == condition]
            calls = [int(s["metrics"].get("rubydex_tool_calls") or 0) for s in group]
            summary[scenario][condition] = {
                "count": len(group),
                "exact_count": sum(1 for s in group if s["score"].get("exact")),
                "selection_correct_count": sum(1 for s in group if s["routing"]["selection_correct"]),
                "semantic_run_count": sum(1 for c in calls if c > 0),
                "semantic_call_total": sum(calls),
                "median_total_tokens": median([s["metrics"].get("total_tokens") for s in group]),
                "median_uncached": median([s["metrics"].get("uncached_input_tokens") for s in group]),
                "median_elapsed": median([s["metrics"].get("elapsed_seconds") for s in group]),
                "median_cost": median([s["metrics"].get("estimated_cost_usd") for s in group]),
                "median_shell": median([s["metrics"].get("command_count") for s in group]),
                "median_search": median([s["metrics"].get("search_command_count") for s in group]),
            }

    condition_summary = {}
    for condition in CONDITIONS:
        group = [s for s in samples if s["meta"]["condition"] == condition]
        calls = [int(s["metrics"].get("rubydex_tool_calls") or 0) for s in group]
        condition_summary[condition] = {
            "count": len(group),
            "exact_count": sum(1 for s in group if s["score"].get("exact")),
            "selection_correct_count": sum(1 for s in group if s["routing"]["selection_correct"]),
            "semantic_run_count": sum(1 for c in calls if c > 0),
            "semantic_call_total": sum(calls),
            "median_total_tokens": median([s["metrics"].get("total_tokens") for s in group]),
            "median_uncached": median([s["metrics"].get("uncached_input_tokens") for s in group]),
            "median_elapsed": median([s["metrics"].get("elapsed_seconds") for s in group]),
            "median_cost": median([s["metrics"].get("estimated_cost_usd") for s in group]),
        }

    result = {
        "lab": "09", "model": args.model, "reasoning": args.reasoning,
        "repository": truth["repository"], "revision": truth["revision"], "target": truth["target"],
        "samples": samples, "summary": summary, "condition_summary": condition_summary,
    }
    (output_root / "report.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Lab 09 — deterministic evidence routing", "",
        f"- Model: `{args.model}`", f"- Reasoning: `{args.reasoning}`",
        f"- Repository: `{truth['repository']}`", f"- Revision: `{truth['revision']}`", "",
        "Expected route: `declaration -> source`; all relationship-set scenarios -> `semantic`.", "",
        "## Per-scenario result", "",
        "| Scenario | Cond | Exact | Route correct | Semantic runs | RDX calls | Shell | Search | Sec | Tokens | Uncached | Cost |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario in SCENARIOS:
        for condition in CONDITIONS:
            s = summary[scenario][condition]
            lines.append(
                f"| {scenario} | {condition} | {s['exact_count']}/{s['count']} | "
                f"{s['selection_correct_count']}/{s['count']} | {s['semantic_run_count']}/{s['count']} | "
                f"{s['semantic_call_total']} | {fmt_num(s['median_shell'])} | {fmt_num(s['median_search'])} | "
                f"{fmt_num(s['median_elapsed'], 1)} | {fmt_num(s['median_total_tokens'])} | "
                f"{fmt_num(s['median_uncached'])} | {fmt_cost(s['median_cost'])} |"
            )

    lines += ["", "## Condition aggregate", "",
        "| Condition | Exact | Route correct | Semantic runs | RDX calls | Median sec | Median tokens | Median uncached | Median cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for condition in CONDITIONS:
        s = condition_summary[condition]
        lines.append(
            f"| {condition} | {s['exact_count']}/{s['count']} | {s['selection_correct_count']}/{s['count']} | "
            f"{s['semantic_run_count']}/{s['count']} | {s['semantic_call_total']} | "
            f"{fmt_num(s['median_elapsed'], 1)} | {fmt_num(s['median_total_tokens'])} | "
            f"{fmt_num(s['median_uncached'])} | {fmt_cost(s['median_cost'])} |"
        )

    lines += ["", "## Interpretation guardrails", "",
        "- E leaves Rubydex optional and gives no tool-selection policy.",
        "- F gives the Lab 08 prose escalation policy but leaves the final tool choice to the agent.",
        "- G is an oracle task-shape router for this controlled ladder: it routes declaration to source-only and relationship-set tasks to required semantic-first evidence.",
        "- G does not test prompt classification. It tests the upper bound of routing once task shape is known.",
        "- Correctness differences without actual Rubydex calls must not be attributed to semantic evidence."]
    report = "\n".join(lines) + "\n"
    (output_root / "report.md").write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
