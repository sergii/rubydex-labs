#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "labs" / "13-evidence-fusion"
FIXTURES = LAB / "fixtures" / "identity-boundary.json"

IDENTITY = {"SAME_AS", "RENAMED_FROM", "MOVED_FROM"}
REPRESENTATION = {"REPRESENTS", "OBSERVED_AS"}
DOMAIN = {"IMPLEMENTED_BY", "OWNED_BY", "SERVES_CAPABILITY", "DERIVED_FROM"}


def classify(relation):
    if relation in IDENTITY:
        return "IDENTITY"
    if relation in REPRESENTATION:
        return "REPRESENTATION"
    if relation == "DEPLOYED_AS":
        return "REPRESENTATION_REVIEW"
    if relation in DOMAIN:
        return "DOMAIN_ASSERTION"
    return "UNKNOWN"


def assertion_for(relation):
    if relation not in DOMAIN:
        return None
    return {
        "schema_version": "1",
        "id": f"AST-LAB13-{relation}",
        "kind": "DECLARED",
        "subject": {"id": "ENT-SUBJECT", "type": "Service"},
        "predicate": relation.lower(),
        "object": {"id": "ENT-OBJECT", "type": "Entity"},
        "scope": {},
        "evidence_refs": ["EVID-LAB13-IDENTITY-BOUNDARY"],
        "recorded_at": "2026-09-14T00:00:00Z",
        "status": "ACTIVE",
    }


def main():
    rows = json.loads(FIXTURES.read_text())
    failures = 0

    for row in rows:
        actual = classify(row["relation"])
        ok = actual == row["expected_class"]
        print(f"{'PASS' if ok else 'FAIL'} classify {row['relation']} expected={row['expected_class']} actual={actual}")
        failures += 0 if ok else 1

        assertion = assertion_for(row["relation"])
        if actual == "DOMAIN_ASSERTION":
            ok = assertion is not None and assertion["predicate"] == row["relation"].lower()
            print(f"{'PASS' if ok else 'FAIL'} assertion {row['relation']}")
            failures += 0 if ok else 1
        else:
            ok = assertion is None
            print(f"{'PASS' if ok else 'FAIL'} no-domain-assertion {row['relation']}")
            failures += 0 if ok else 1

    # Ownership can change without changing service identity.
    service_id = "ENT-SERVICE-CHECKOUT"
    owner_a = {
        "subject": {"id": service_id, "type": "Service"},
        "predicate": "owned_by",
        "object": {"id": "ENT-TEAM-A", "type": "Team"},
        "valid_time": {"from": "2026-01-01T00:00:00Z", "to": "2026-06-30T23:59:59Z"},
    }
    owner_b = {
        "subject": {"id": service_id, "type": "Service"},
        "predicate": "owned_by",
        "object": {"id": "ENT-TEAM-B", "type": "Team"},
        "valid_time": {"from": "2026-07-01T00:00:00Z", "to": None},
    }
    ok = owner_a["subject"]["id"] == owner_b["subject"]["id"] and owner_a["object"]["id"] != owner_b["object"]["id"]
    print(f"{'PASS' if ok else 'FAIL'} ownership-change-preserves-service-identity")
    failures += 0 if ok else 1

    print(f"tests_complete failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
