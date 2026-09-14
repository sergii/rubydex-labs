#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
FIXTURES = LAB / "fixtures" / "comparisons.json"
RULES = LAB / "fixtures" / "predicate-rules.json"
BUILDER = LAB / "scripts" / "build-comparison-record.py"

ACTIVE_ALLOWED = {"CONTRADICTION", "DECLARED_VS_OBSERVED_DRIFT"}
BENIGN_CLASSES = {
    "COMPATIBLE",
    "NON_COMPARABLE_PREDICATE",
    "IDENTITY_UNRESOLVED",
    "SCOPE_MISMATCH",
    "TEMPORAL_MISMATCH",
    "REVISION_MISMATCH",
    "ENVIRONMENT_MISMATCH",
    "INSUFFICIENT_EVIDENCE",
}


def main():
    proc = subprocess.run(
        [sys.executable, str(BUILDER), str(FIXTURES), str(RULES)],
        check=True,
        capture_output=True,
        text=True,
    )
    records = json.loads(proc.stdout)
    failures = 0

    for record in records:
        cls = record["comparison_class"]
        state = record["conflict_state"]
        conflict_ref = record["conflict_ref"]

        ok = True
        if cls in BENIGN_CLASSES:
            ok = state == "NONE" and conflict_ref is None
        elif cls in ACTIVE_ALLOWED:
            ok = state == "ACTIVE" and isinstance(conflict_ref, str) and conflict_ref

        if not record["assertion_refs"] or len(record["assertion_refs"]) < 2:
            ok = False
        if "identity" not in record["aligned_dimensions"]:
            ok = False
        if "predicate" not in record["aligned_dimensions"]:
            ok = False

        print(f"{'PASS' if ok else 'FAIL'} {record['id']} class={cls} conflict_state={state}")
        if not ok:
            failures += 1

    print(f"comparison_records={len(records)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
