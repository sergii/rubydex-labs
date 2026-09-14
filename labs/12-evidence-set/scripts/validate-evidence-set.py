#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED_TOP = {
    "schema_version",
    "evidence_class",
    "query",
    "target",
    "complete",
    "count",
    "items",
    "provenance",
}


def validate(evidence_set):
    errors = []

    missing = sorted(REQUIRED_TOP - set(evidence_set.keys()))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
        return errors

    if evidence_set.get("schema_version") != "1":
        errors.append("schema_version must be '1'")

    items = evidence_set.get("items")
    if not isinstance(items, list):
        errors.append("items must be an array")
        return errors

    count = evidence_set.get("count")
    if not isinstance(count, int) or count < 0:
        errors.append("count must be a non-negative integer")
    elif count != len(items):
        errors.append(f"count mismatch: count={count}, items.length={len(items)}")

    keys = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] must be an object")
            continue
        key = item.get("key")
        if not isinstance(key, str) or not key:
            errors.append(f"items[{index}].key must be a non-empty string")
        else:
            keys.append(key)

    duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
    if duplicate_keys:
        errors.append(f"duplicate item keys: {', '.join(duplicate_keys)}")

    if not isinstance(evidence_set.get("complete"), bool):
        errors.append("complete must be boolean")

    provenance = evidence_set.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        backend = provenance.get("backend")
        if not isinstance(backend, str) or not backend:
            errors.append("provenance.backend must be a non-empty string")

    scope = evidence_set.get("scope")
    if scope is not None and not isinstance(scope, dict):
        errors.append("scope must be an object when present")

    return errors


def load_records(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return data
    return [{"id": Path(path).stem, "evidence_set": data}]


def main():
    if len(sys.argv) != 2:
        print("usage: validate-evidence-set.py <fixtures-or-evidence-set.json>", file=sys.stderr)
        return 2

    failures = 0
    records = load_records(sys.argv[1])
    for record in records:
        fixture_id = record.get("id", "unknown")
        evidence_set = record.get("evidence_set", record)
        errors = validate(evidence_set)
        if errors:
            failures += 1
            print(f"FAIL {fixture_id}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {fixture_id} count={evidence_set['count']} complete={str(evidence_set['complete']).lower()}")

    print(f"fixtures={len(records)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
