#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_time(value):
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def intervals_overlap(a, b):
    if not a or not b:
        return True
    a_from = parse_time(a.get("from"))
    a_to = parse_time(a.get("to"))
    b_from = parse_time(b.get("from"))
    b_to = parse_time(b.get("to"))
    if a_to is not None and b_from is not None and a_to < b_from:
        return False
    if b_to is not None and a_from is not None and b_to < a_from:
        return False
    return True


def entity_object(obj):
    return isinstance(obj, dict) and "id" in obj and "type" in obj


def scalar_value(obj):
    return obj.get("value") if isinstance(obj, dict) and "value" in obj else None


def same_entity(a, b):
    return a.get("id") == b.get("id")


def load_rules(path):
    data = json.loads(Path(path).read_text())
    return {(r["left"], r["right"]): r["relation"] for r in data["pairs"]}


def scope_mismatch(left, right, field):
    l = (left.get("scope") or {}).get(field)
    r = (right.get("scope") or {}).get(field)
    return l is not None and r is not None and l != r


def classify(left, right, rules):
    if not same_entity(left["subject"], right["subject"]):
        return "IDENTITY_UNRESOLVED"

    if scope_mismatch(left, right, "environment"):
        return "ENVIRONMENT_MISMATCH"
    if scope_mismatch(left, right, "revision"):
        return "REVISION_MISMATCH"
    if scope_mismatch(left, right, "service"):
        return "SCOPE_MISMATCH"

    if not intervals_overlap(left.get("valid_time"), right.get("valid_time")):
        return "TEMPORAL_MISMATCH"

    pred_relation = rules.get((left["predicate"], right["predicate"]), "NON_COMPARABLE")
    if pred_relation == "NON_COMPARABLE":
        return "NON_COMPARABLE_PREDICATE"

    lobj = left["object"]
    robj = right["object"]

    if left["predicate"] == "allowed_dependency_only" and right["predicate"] == "called":
        if entity_object(lobj) and entity_object(robj) and not same_entity(lobj, robj):
            return "DECLARED_VS_OBSERVED_DRIFT"
        return "COMPATIBLE"
    if right["predicate"] == "allowed_dependency_only" and left["predicate"] == "called":
        if entity_object(lobj) and entity_object(robj) and not same_entity(lobj, robj):
            return "DECLARED_VS_OBSERVED_DRIFT"
        return "COMPATIBLE"

    if pred_relation in ("EQUIVALENT", "COMPATIBLE_DIFFERENT_TRUTH_DOMAIN"):
        if entity_object(lobj) and entity_object(robj):
            return "COMPATIBLE" if same_entity(lobj, robj) else "INSUFFICIENT_EVIDENCE"
        return "COMPATIBLE" if scalar_value(lobj) == scalar_value(robj) else "INSUFFICIENT_EVIDENCE"

    if pred_relation == "POTENTIALLY_CONTRADICTORY":
        if entity_object(lobj) and entity_object(robj):
            return "COMPATIBLE" if same_entity(lobj, robj) else "CONTRADICTION"
        return "COMPATIBLE" if scalar_value(lobj) == scalar_value(robj) else "CONTRADICTION"

    return "INSUFFICIENT_EVIDENCE"


def main():
    if len(sys.argv) != 3:
        print("usage: compare-assertions.py <comparisons.json> <predicate-rules.json>", file=sys.stderr)
        return 2

    rows = json.loads(Path(sys.argv[1]).read_text())
    rules = load_rules(sys.argv[2])
    failures = 0

    for row in rows:
        actual = classify(row["left"], row["right"], rules)
        ok = actual == row["expected"]
        print(f"{'PASS' if ok else 'FAIL'} {row['id']} expected={row['expected']} actual={actual}")
        if not ok:
            failures += 1

    print(f"fixtures={len(rows)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
