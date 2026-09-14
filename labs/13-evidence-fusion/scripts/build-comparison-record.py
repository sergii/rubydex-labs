#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from importlib.util import spec_from_file_location, module_from_spec

LAB = Path(__file__).resolve().parents[1]
COMPARE = LAB / "scripts" / "compare-assertions.py"

spec = spec_from_file_location("compare_assertions", COMPARE)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)


def alignment_state(left, right, field):
    l = (left.get("scope") or {}).get(field)
    r = (right.get("scope") or {}).get(field)
    if l is None and r is None:
        return "NOT_APPLICABLE"
    if l is None or r is None:
        return "UNKNOWN"
    return "ALIGNED" if l == r else "MISMATCHED"


def identity_state(left, right):
    return "ALIGNED" if mod.same_entity(left["subject"], right["subject"]) else "MISMATCHED"


def predicate_state(left, right, rules):
    relation = rules.get((left["predicate"], right["predicate"]), "NON_COMPARABLE")
    return "MISMATCHED" if relation == "NON_COMPARABLE" else "ALIGNED"


def valid_time_state(left, right):
    a = left.get("valid_time")
    b = right.get("valid_time")
    if not a and not b:
        return "NOT_APPLICABLE"
    if not a or not b:
        return "UNKNOWN"
    return "ALIGNED" if mod.intervals_overlap(a, b) else "MISMATCHED"


def truth_domain_state(left, right):
    return "ALIGNED" if left.get("kind") == right.get("kind") else "NOT_APPLICABLE"


def conflict_state(comparison_class):
    if comparison_class == "CONTRADICTION":
        return "ACTIVE"
    if comparison_class == "DECLARED_VS_OBSERVED_DRIFT":
        return "ACTIVE"
    return "NONE"


def build(row, rules):
    left = row["left"]
    right = row["right"]
    comparison_class = mod.classify(left, right, rules)
    return {
        "schema_version": "1",
        "id": f"CMP-{row['id']}",
        "assertion_refs": [left["id"], right["id"]],
        "comparison_class": comparison_class,
        "conflict_state": conflict_state(comparison_class),
        "aligned_dimensions": {
            "identity": identity_state(left, right),
            "predicate": predicate_state(left, right, rules),
            "scope": alignment_state(left, right, "service"),
            "revision": alignment_state(left, right, "revision"),
            "environment": alignment_state(left, right, "environment"),
            "valid_time": valid_time_state(left, right),
            "truth_domain": truth_domain_state(left, right),
        },
        "reason": row.get("description"),
        "evidence_refs": sorted(set(left.get("evidence_refs", []) + right.get("evidence_refs", []))),
        "conflict_ref": f"CONFLICT-{row['id']}" if conflict_state(comparison_class) == "ACTIVE" else None,
        "finding_ref": None,
        "recorded_at": "2026-09-14T00:00:00Z",
        "metadata": {"fixture_id": row["id"]},
    }


def main():
    if len(sys.argv) not in (3, 4):
        print("usage: build-comparison-record.py <comparisons.json> <predicate-rules.json> [fixture-id]", file=sys.stderr)
        return 2

    rows = json.loads(Path(sys.argv[1]).read_text())
    rules = mod.load_rules(sys.argv[2])
    if len(sys.argv) == 4:
        rows = [row for row in rows if row["id"] == sys.argv[3]]
        if len(rows) != 1:
            print("fixture-id must match exactly one row", file=sys.stderr)
            return 2

    payload = [build(row, rules) for row in rows]
    print(json.dumps(payload[0] if len(payload) == 1 else payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
