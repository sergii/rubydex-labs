#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "runtime-observations.json"


def has_resolved_entity(value):
    return isinstance(value, dict) and bool(value.get("id")) and bool(value.get("type"))


def decide(observation):
    window = observation.get("window")
    if not isinstance(window, dict) or not window.get("from") or not window.get("to"):
        return "REFUSE_ASSERTION", None

    subject = observation.get("subject")
    obj = observation.get("object")
    if not has_resolved_entity(subject):
        return "REQUIRE_IDENTITY_RESOLUTION", None
    if isinstance(obj, dict) and "representation" in obj and not has_resolved_entity(obj):
        return "REQUIRE_IDENTITY_RESOLUTION", None

    coverage = observation.get("coverage", "UNKNOWN")
    observed = observation.get("observed")
    if observed is False and coverage != "COMPLETE_FOR_SCOPE":
        return "REFUSE_ASSERTION", None

    assertion = {
        "schema_version": "1",
        "id": f"AST-RUNTIME-{observation['backend']}-{window['from']}",
        "kind": "OBSERVED",
        "subject": copy.deepcopy(subject),
        "predicate": observation["predicate"],
        "object": copy.deepcopy(obj),
        "scope": {
            "repository": None,
            "revision": None,
            "environment": observation.get("environment"),
            "service": subject.get("name"),
            "filters": list(observation.get("filters", [])),
        },
        "valid_time": {"from": window["from"], "to": window["to"]},
        "recorded_at": window["to"],
        "evidence_refs": list(observation.get("evidence_refs", [])),
        "status": "ACTIVE",
        "metadata": {
            "runtime_backend": observation["backend"],
            "coverage": coverage,
            "sample_count": observation.get("sample_count"),
            "sampling_rate": observation.get("sampling_rate"),
            "observed": observed,
        },
    }
    return "ASSERT", assertion


def main():
    rows = json.loads(FIXTURES.read_text())
    failures = 0
    assertions = 0
    for row in rows:
        before = copy.deepcopy(row["observation"])
        actual, assertion = decide(row["observation"])
        ok = actual == row["expected"]
        checks = []
        if assertion:
            assertions += 1
            checks.extend([
                assertion["kind"] == "OBSERVED",
                assertion["valid_time"] == row["observation"]["window"],
                assertion["scope"]["environment"] == row["observation"].get("environment"),
                assertion["scope"]["filters"] == row["observation"].get("filters", []),
                assertion["evidence_refs"] == row["observation"].get("evidence_refs", []),
                assertion["metadata"]["coverage"] == row["observation"].get("coverage"),
                assertion["metadata"]["sampling_rate"] == row["observation"].get("sampling_rate"),
            ])
            ok = ok and all(checks)
        ok = ok and row["observation"] == before
        print(f"{'PASS' if ok else 'FAIL'} {row['id']} expected={row['expected']} actual={actual}")
        failures += 0 if ok else 1

    # Mutation guardrail: sampled absence must stay refused even with large sample count.
    base = next(r["observation"] for r in rows if r["id"] == "sampled-call-absent")
    mutated = copy.deepcopy(base)
    mutated["sample_count"] = 1_000_000
    mutated["sampling_rate"] = 0.99
    actual, _ = decide(mutated)
    ok = actual == "REFUSE_ASSERTION"
    print(f"{'PASS' if ok else 'FAIL'} sampled-absence-large-sample expected=REFUSE_ASSERTION actual={actual}")
    failures += 0 if ok else 1

    # Mutation guardrail: completeness is scoped; changing scope does not authorize extrapolation.
    complete = next(r["observation"] for r in rows if r["id"] == "complete-zero-events")
    mutated = copy.deepcopy(complete)
    mutated["coverage"] = "PARTIAL"
    mutated["observed"] = False
    actual, _ = decide(mutated)
    ok = actual == "REFUSE_ASSERTION"
    print(f"{'PASS' if ok else 'FAIL'} partial-zero-events expected=REFUSE_ASSERTION actual={actual}")
    failures += 0 if ok else 1

    print(f"fixtures={len(rows)} assertions={assertions} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
