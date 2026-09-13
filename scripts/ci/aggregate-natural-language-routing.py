#!/usr/bin/env python3
"""Aggregate Lab 10 natural-language evidence-routing benchmark."""
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

CONDITIONS = ("H", "O")
CLASS_TO_ROUTE = {
    "SOURCE_LOCAL": "source",
    "SEMANTIC_RELATIONSHIP_SET": "semantic",
    "RUNTIME_BEHAVIOR": "runtime",
    "ARCHITECTURE_KNOWLEDGE": "architecture",
}


def median(values):
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def fmt_num(value, digits=0):
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}" if digits else f"{value:,.0f}"


def fmt_cost(value):
    return "n/a" if value is None else f"${value:.4f}"


def classifier_metrics(payload: dict, model: str) -> dict:
    usage = payload.get("usage") or {}
    metrics = {
        "usage_found": bool(usage),
        "input_tokens": int(usage.get("input_tokens") or 0),
        "cached_input_tokens": int(usage.get("cached_input_tokens") or 0),
        "uncached_input_tokens": int(usage.get("uncached_input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "reasoning_output_tokens": int(usage.get("reasoning_output_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
        "elapsed_seconds": payload.get("elapsed_seconds"),
    }
    metrics["estimated_cost_usd"] = helper.estimated_cost(model, metrics)
    return metrics


def zero_agent_metrics() -> dict:
    return {
        "usage_found": False,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "uncached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "total_tokens": 0,
        "elapsed_seconds": None,
        "estimated_cost_usd": None,
        "rubydex_tool_calls": 0,
        "command_count": 0,
        "search_command_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="downstream agent model")
    parser.add_argument("--classifier-model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    requests = json.loads((ROOT / "labs/10-natural-language-evidence-routing/requests.json").read_text())
    request_by_id = {item["id"]: item for item in requests}
    truth = json.loads((ROOT / "labs/07-task-shape-boundary/ground-truth.json").read_text())
    artifacts_root = Path(args.artifacts)
    logs_root = Path(args.logs)
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    samples = []
    for meta_path in sorted(artifacts_root.glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text())
        task = request_by_id[meta["task_id"]]
        condition = meta["condition"]
        repeat = int(meta["repeat"])
        expected_class = task["expected_class"]
        scenario = task.get("scenario")
        classifier_path = meta_path.parent / "classifier.json"
        classifier_payload = json.loads(classifier_path.read_text()) if classifier_path.exists() else {}
        predicted_class = classifier_payload.get("predicted_class")
        selected_route = CLASS_TO_ROUTE.get(predicted_class, "unknown")
        expected_route = CLASS_TO_ROUTE[expected_class]
        cmetrics = classifier_metrics(classifier_payload, args.classifier_model)

        job_name = f"sample-{task['id']}-{condition}-r{repeat}"
        log_path = logs_root / f"{job_name}.log"
        agent_metrics = zero_agent_metrics()
        score = None
        observed_route_correct = None
        if scenario:
            agent_metrics = helper.parse_codex_log(log_path)
            agent_metrics["estimated_cost_usd"] = helper.estimated_cost(args.model, agent_metrics)
            agent_metrics.update(nav.parse_navigation(log_path))
            final_path = meta_path.parent / "final.txt"
            final = final_path.read_text(errors="replace") if final_path.exists() else ""
            score = helper.score_sample(scenario, final, truth) if final else {"exact": False, "parse_error": "downstream agent not run"}
            observed_semantic = (agent_metrics.get("rubydex_tool_calls") or 0) > 0
            if selected_route in {"source", "semantic"} and final:
                observed_route_correct = observed_semantic == (selected_route == "semantic")
            else:
                observed_route_correct = False

        classifier_cost = cmetrics.get("estimated_cost_usd") or 0.0
        agent_cost = agent_metrics.get("estimated_cost_usd") or 0.0
        samples.append({
            "job_name": job_name,
            "meta": meta,
            "request": task["request"],
            "expected_class": expected_class,
            "predicted_class": predicted_class,
            "classification_correct": predicted_class == expected_class,
            "expected_route": expected_route,
            "selected_route": selected_route,
            "route_correct": selected_route == expected_route,
            "scenario": scenario,
            "classifier": classifier_payload,
            "classifier_metrics": cmetrics,
            "agent_metrics": agent_metrics,
            "score": score,
            "observed_route_correct": observed_route_correct,
            "combined_cost_usd": classifier_cost + agent_cost,
        })

    if not samples:
        raise SystemExit("No sample artifacts found")

    class_summary = {}
    for evidence_class in CLASS_TO_ROUTE:
        group = [s for s in samples if s["meta"]["condition"] == "H" and s["expected_class"] == evidence_class]
        class_summary[evidence_class] = {
            "count": len(group),
            "correct": sum(1 for s in group if s["classification_correct"]),
            "median_tokens": median([s["classifier_metrics"].get("total_tokens") for s in group]),
            "median_elapsed": median([s["classifier_metrics"].get("elapsed_seconds") for s in group]),
            "median_cost": median([s["classifier_metrics"].get("estimated_cost_usd") for s in group]),
        }

    condition_summary = {}
    for condition in CONDITIONS:
        group = [s for s in samples if s["meta"]["condition"] == condition]
        executable = [s for s in group if s["scenario"]]
        condition_summary[condition] = {
            "count": len(group),
            "classification_correct": sum(1 for s in group if s["classification_correct"]),
            "route_correct": sum(1 for s in group if s["route_correct"]),
            "classifier_median_tokens": median([s["classifier_metrics"].get("total_tokens") for s in group]),
            "classifier_median_elapsed": median([s["classifier_metrics"].get("elapsed_seconds") for s in group]),
            "classifier_median_cost": median([s["classifier_metrics"].get("estimated_cost_usd") for s in group]),
            "executable_count": len(executable),
            "downstream_exact": sum(1 for s in executable if s["score"] and s["score"].get("exact")),
            "observed_route_correct": sum(1 for s in executable if s["observed_route_correct"]),
            "agent_median_tokens": median([s["agent_metrics"].get("total_tokens") for s in executable]),
            "agent_median_elapsed": median([s["agent_metrics"].get("elapsed_seconds") for s in executable]),
            "agent_median_cost": median([s["agent_metrics"].get("estimated_cost_usd") for s in executable]),
            "combined_median_cost": median([s["combined_cost_usd"] for s in executable]),
        }

    task_summary = {}
    for task in requests:
        if not task.get("scenario"):
            continue
        task_summary[task["id"]] = {}
        for condition in CONDITIONS:
            group = [s for s in samples if s["meta"]["task_id"] == task["id"] and s["meta"]["condition"] == condition]
            task_summary[task["id"]][condition] = {
                "count": len(group),
                "route_correct": sum(1 for s in group if s["route_correct"]),
                "exact": sum(1 for s in group if s["score"] and s["score"].get("exact")),
                "median_agent_tokens": median([s["agent_metrics"].get("total_tokens") for s in group]),
                "median_combined_cost": median([s["combined_cost_usd"] for s in group]),
            }

    result = {
        "lab": "10",
        "model": args.model,
        "classifier_model": args.classifier_model,
        "reasoning": args.reasoning,
        "repository": truth["repository"],
        "revision": truth["revision"],
        "target": truth["target"],
        "samples": samples,
        "class_summary": class_summary,
        "condition_summary": condition_summary,
        "task_summary": task_summary,
    }
    (output_root / "report.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Lab 10 — natural-language evidence routing",
        "",
        f"- Classifier model: `{args.classifier_model}` (reasoning: `low`)",
        f"- Downstream model: `{args.model}` (reasoning: `{args.reasoning}`)",
        f"- Repository: `{truth['repository']}`",
        f"- Revision: `{truth['revision']}`",
        "",
        "## Classifier accuracy (H)",
        "",
        "| Expected class | Correct | Median sec | Median tokens | Median cost |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for evidence_class, s in class_summary.items():
        lines.append(
            f"| {evidence_class} | {s['correct']}/{s['count']} | {fmt_num(s['median_elapsed'], 2)} | "
            f"{fmt_num(s['median_tokens'])} | {fmt_cost(s['median_cost'])} |"
        )

    lines += [
        "",
        "## Condition aggregate",
        "",
        "| Cond | Class correct | Route correct | Downstream exact | Observed route | Classifier tokens | Classifier cost | Agent tokens | Agent cost | Combined cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in CONDITIONS:
        s = condition_summary[condition]
        lines.append(
            f"| {condition} | {s['classification_correct']}/{s['count']} | {s['route_correct']}/{s['count']} | "
            f"{s['downstream_exact']}/{s['executable_count']} | {s['observed_route_correct']}/{s['executable_count']} | "
            f"{fmt_num(s['classifier_median_tokens'])} | {fmt_cost(s['classifier_median_cost'])} | "
            f"{fmt_num(s['agent_median_tokens'])} | {fmt_cost(s['agent_median_cost'])} | {fmt_cost(s['combined_median_cost'])} |"
        )

    lines += [
        "",
        "## Executable task detail",
        "",
        "| Task | Cond | Route correct | Exact | Median agent tokens | Median combined cost |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for task in requests:
        if not task.get("scenario"):
            continue
        for condition in CONDITIONS:
            s = task_summary[task["id"]][condition]
            lines.append(
                f"| {task['id']} | {condition} | {s['route_correct']}/{s['count']} | {s['exact']}/{s['count']} | "
                f"{fmt_num(s['median_agent_tokens'])} | {fmt_cost(s['median_combined_cost'])} |"
            )

    misses = [s for s in samples if s["meta"]["condition"] == "H" and not s["classification_correct"]]
    lines += ["", "## Classifier misses", ""]
    if not misses:
        lines.append("No classifier misses.")
    else:
        for s in misses:
            lines.append(f"- `{s['meta']['task_id']}`: expected `{s['expected_class']}`, predicted `{s['predicted_class']}`")

    lines += [
        "",
        "## Guardrails",
        "",
        "- O is an oracle upper bound; it receives the hidden expected class.",
        "- H receives only the raw request plus class definitions; expected labels are never sent to the classifier.",
        "- Runtime and architecture requests are classification-only because those evidence backends are not wired into this repository yet.",
        "- Downstream source/semantic tasks reuse the frozen Lab 07 ground truth so routing, not answer style, remains the manipulated variable.",
    ]
    report = "\n".join(lines) + "\n"
    (output_root / "report.md").write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
