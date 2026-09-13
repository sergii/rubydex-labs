#!/usr/bin/env python3
"""Score one Lab 11 EvidencePlan or validate the frozen corpus offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSES = {
    "SOURCE_LOCAL",
    "SEMANTIC_RELATIONSHIP_SET",
    "RUNTIME_BEHAVIOR",
    "ARCHITECTURE_KNOWLEDGE",
}
EXPECTED_BACKEND = {
    "SOURCE_LOCAL": "source",
    "SEMANTIC_RELATIONSHIP_SET": "rubydex",
    "RUNTIME_BEHAVIOR": "runtime_observability",
    "ARCHITECTURE_KNOWLEDGE": "architecture_knowledge",
}


def load_truth(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text())
    return {item["id"]: item for item in payload["tasks"]}


def validate_corpus(requests_path: Path, truth_path: Path) -> None:
    requests = json.loads(requests_path.read_text())
    truth = load_truth(truth_path)
    request_ids = [item["id"] for item in requests]
    if len(request_ids) != len(set(request_ids)):
        raise SystemExit("duplicate request ids")
    if set(request_ids) != set(truth):
        raise SystemExit("request ids and ground-truth ids differ")
    for task_id, item in truth.items():
        required = set(item["required_classes"])
        optional = set(item["optional_classes"])
        if not required:
            raise SystemExit(f"{task_id}: at least one required class is required")
        if not required <= CLASSES or not optional <= CLASSES:
            raise SystemExit(f"{task_id}: unknown evidence class")
        if required & optional:
            raise SystemExit(f"{task_id}: required/optional classes overlap")
        if item["strategy"] not in {"parallel_when_possible", "sequential"}:
            raise SystemExit(f"{task_id}: invalid strategy")
    print(f"OK: {len(request_ids)} frozen requests")


def score(task_id: str, result_path: Path, truth_path: Path) -> dict:
    truth = load_truth(truth_path)[task_id]
    result = json.loads(result_path.read_text())
    plan = result["plan"]
    steps = plan.get("steps") or []

    predicted_classes = [step.get("evidence_class") for step in steps]
    duplicates = sorted({c for c in predicted_classes if predicted_classes.count(c) > 1})
    backend_mismatches = [
        step.get("evidence_class")
        for step in steps
        if EXPECTED_BACKEND.get(step.get("evidence_class")) != step.get("backend")
    ]

    predicted_required = {
        step["evidence_class"] for step in steps if step.get("requirement") == "required"
    }
    predicted_optional = {
        step["evidence_class"] for step in steps if step.get("requirement") == "optional"
    }
    expected_required = set(truth["required_classes"])
    allowed_optional = set(truth["optional_classes"])
    allowed_all = expected_required | allowed_optional

    required_tp = predicted_required & expected_required
    missed_required = expected_required - predicted_required
    extra_required = predicted_required - expected_required
    forbidden_selected = (predicted_required | predicted_optional) - allowed_all
    invalid_optional = predicted_optional - allowed_optional

    required_recall = len(required_tp) / len(expected_required)
    exact_required_set = predicted_required == expected_required
    no_overrouting = not forbidden_selected and not invalid_optional
    strategy_match = plan.get("strategy") == truth["strategy"]
    exact_plan_shape = (
        exact_required_set
        and no_overrouting
        and not duplicates
        and not backend_mismatches
        and strategy_match
    )

    return {
        "task_id": task_id,
        "required_recall": required_recall,
        "exact_required_set": exact_required_set,
        "no_overrouting": no_overrouting,
        "strategy_match": strategy_match,
        "exact_plan_shape": exact_plan_shape,
        "expected_required": sorted(expected_required),
        "predicted_required": sorted(predicted_required),
        "allowed_optional": sorted(allowed_optional),
        "predicted_optional": sorted(predicted_optional),
        "missed_required": sorted(missed_required),
        "extra_required": sorted(extra_required),
        "forbidden_selected": sorted(forbidden_selected),
        "duplicate_classes": duplicates,
        "backend_mismatches": sorted(c for c in backend_mismatches if c),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--task-id")
    parser.add_argument("--result")
    parser.add_argument("--output")
    parser.add_argument(
        "--requests",
        default=str(ROOT / "labs/11-evidence-planner/requests.json"),
    )
    parser.add_argument(
        "--ground-truth",
        default=str(ROOT / "labs/11-evidence-planner/ground-truth.json"),
    )
    args = parser.parse_args()

    requests_path = Path(args.requests)
    truth_path = Path(args.ground_truth)

    if args.self_check:
        validate_corpus(requests_path, truth_path)
        return 0

    if not args.task_id or not args.result or not args.output:
        raise SystemExit("--task-id, --result, and --output are required unless --self-check is used")

    payload = score(args.task_id, Path(args.result), truth_path)
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
