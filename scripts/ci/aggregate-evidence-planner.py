#!/usr/bin/env python3
"""Aggregate Lab 11 planner-only benchmark artifacts."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]


def load_helper():
    path = ROOT / "scripts/ci/aggregate-task-shape.py"
    spec = importlib.util.spec_from_file_location("task_shape_aggregate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


helper = load_helper()


def median(values):
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def fmt(value, digits=0):
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    samples = []
    for result_path in sorted(Path(args.artifacts).rglob("planner-result.json")):
        sample_dir = result_path.parent
        score_path = sample_dir / "score.json"
        meta_path = sample_dir / "meta.json"
        if not score_path.exists() or not meta_path.exists():
            continue
        result = json.loads(result_path.read_text())
        score = json.loads(score_path.read_text())
        meta = json.loads(meta_path.read_text())
        usage = result.get("usage") or {}
        metrics = {
            "usage_found": bool(usage),
            "input_tokens": int(usage.get("input_tokens") or 0),
            "cached_input_tokens": int(usage.get("cached_input_tokens") or 0),
            "uncached_input_tokens": int(usage.get("uncached_input_tokens") or 0),
            "output_tokens": int(usage.get("output_tokens") or 0),
            "reasoning_output_tokens": int(usage.get("reasoning_output_tokens") or 0),
            "total_tokens": int(usage.get("total_tokens") or 0),
            "elapsed_seconds": result.get("elapsed_seconds"),
        }
        metrics["estimated_cost_usd"] = helper.estimated_cost(result.get("model"), metrics)
        samples.append({"meta": meta, "score": score, "metrics": metrics})

    if not samples:
        raise SystemExit("no Lab 11 sample artifacts found")

    total = len(samples)
    exact_required = sum(bool(s["score"].get("exact_required_set")) for s in samples)
    exact_plan = sum(bool(s["score"].get("exact_plan_shape")) for s in samples)
    no_overrouting = sum(bool(s["score"].get("no_overrouting")) for s in samples)
    strategy_match = sum(bool(s["score"].get("strategy_match")) for s in samples)
    recall = sum(float(s["score"].get("required_recall") or 0.0) for s in samples) / total

    cost_values = [s["metrics"].get("estimated_cost_usd") for s in samples]
    known_cost = [v for v in cost_values if v is not None]

    lines = [
        "# Lab 11 — evidence planner benchmark",
        "",
        "> This report is generated only after the gated real-API benchmark runs.",
        "",
        "## Correctness",
        "",
        f"- samples: **{total}**",
        f"- required-class recall: **{recall:.1%}**",
        f"- exact required-class set: **{exact_required}/{total}**",
        f"- no over-routing: **{no_overrouting}/{total}**",
        f"- strategy match: **{strategy_match}/{total}**",
        f"- exact plan shape: **{exact_plan}/{total}**",
        "",
        "## Efficiency",
        "",
        f"- median elapsed: **{fmt(median([s['metrics'].get('elapsed_seconds') for s in samples]), 2)} s**",
        f"- median total tokens: **{fmt(median([s['metrics'].get('total_tokens') for s in samples]))}**",
        f"- median uncached input tokens: **{fmt(median([s['metrics'].get('uncached_input_tokens') for s in samples]))}**",
        f"- median output tokens: **{fmt(median([s['metrics'].get('output_tokens') for s in samples]))}**",
        f"- estimated total API cost: **${sum(known_cost):.4f}**" if known_cost else "- estimated total API cost: **n/a**",
        "",
        "## Per task",
        "",
        "| Task | Samples | Exact required set | Exact plan | Mean required recall |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    task_ids = sorted({s["meta"]["task_id"] for s in samples})
    for task_id in task_ids:
        group = [s for s in samples if s["meta"]["task_id"] == task_id]
        group_exact_required = sum(bool(s["score"].get("exact_required_set")) for s in group)
        group_exact_plan = sum(bool(s["score"].get("exact_plan_shape")) for s in group)
        group_recall = sum(float(s["score"].get("required_recall") or 0.0) for s in group) / len(group)
        lines.append(
            f"| {task_id} | {len(group)} | {group_exact_required}/{len(group)} | "
            f"{group_exact_plan}/{len(group)} | {group_recall:.1%} |"
        )

    lines += [
        "",
        "## Interpretation guardrail",
        "",
        "This lab measures planning quality only. It does not prove that the selected backends return correct evidence or that a downstream reasoner uses that evidence correctly.",
        "",
    ]

    Path(args.output).write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
