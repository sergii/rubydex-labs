#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FINDING_MAP = {
    "DECLARED_VS_OBSERVED_DRIFT": ("ARCHITECTURE_DRIFT", "MEDIUM"),
    "CONTRADICTION": ("EVIDENCE_CONFLICT", "MEDIUM"),
}


def uniq(values):
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def build(comparison, assertions_by_id):
    if comparison["conflict_state"] != "ACTIVE":
        return None
    if comparison["comparison_class"] not in FINDING_MAP:
        return None

    refs = comparison["assertion_refs"]
    assertions = [assertions_by_id[ref] for ref in refs]
    finding_class, severity = FINDING_MAP[comparison["comparison_class"]]
    subject_refs = uniq(a["subject"]["id"] for a in assertions)
    evidence_refs = uniq(
        evidence
        for assertion in assertions
        for evidence in assertion.get("evidence_refs", [])
    )
    conflict_refs = [comparison["conflict_ref"]] if comparison.get("conflict_ref") else []
    recorded_at = comparison["recorded_at"]

    return {
        "schema_version": "1",
        "id": f"FINDING-{comparison['id']}",
        "finding_class": finding_class,
        "title": (
            "Declared architecture differs from observed behavior"
            if finding_class == "ARCHITECTURE_DRIFT"
            else "Aligned evidence contains a contradiction"
        ),
        "summary": comparison.get("reason"),
        "status": "OPEN",
        "severity": severity,
        "confidence_record": {
            "schema_version": "1",
            "state": "SUPPORTED",
            "score": None,
            "source_strength": "STRONG",
            "completeness": "UNKNOWN",
            "freshness": "CURRENT",
            "scope_match": "MATCHED",
            "identity_resolution": "RESOLVED",
            "corroboration": "MULTIPLE_SOURCES",
            "contradiction": "PRESENT",
            "calibration": None,
            "method": "DETERMINISTIC_RULE",
            "explanation": "Finding candidate projected from an active ComparisonRecord; severity is not confidence."
        },
        "subject_entity_refs": subject_refs,
        "affected_entity_refs": [],
        "assertion_refs": refs,
        "comparison_refs": [comparison["id"]],
        "conflict_refs": conflict_refs,
        "risk_refs": [],
        "evidence_refs": evidence_refs,
        "policy_refs": [],
        "change_refs": [],
        "incident_refs": [],
        "owner_refs": [],
        "impact": None,
        "blast_radius": None,
        "verification": [{
            "description": "Collect or re-check the authoritative evidence needed to confirm the active comparison remains valid.",
            "evidence_class": None
        }],
        "suggested_actions": [{
            "kind": "INVESTIGATE",
            "description": "Investigate the active evidence disagreement before taking remediation action."
        }],
        "first_seen_at": recorded_at,
        "last_seen_at": recorded_at,
        "resolved_at": None,
        "fingerprint": f"comparison:{comparison['id']}:{comparison['comparison_class']}",
        "supersedes": None,
        "metadata": {"projection": "comparison_to_finding_candidate"}
    }


def main():
    if len(sys.argv) != 3:
        print("usage: build-finding-candidate.py <comparison.json> <assertions.json>", file=sys.stderr)
        return 2
    comparison = json.loads(Path(sys.argv[1]).read_text())
    assertions = json.loads(Path(sys.argv[2]).read_text())
    assertions_by_id = {a["id"]: a for a in assertions}
    missing = [ref for ref in comparison["assertion_refs"] if ref not in assertions_by_id]
    if missing:
        print(f"missing source assertions: {', '.join(missing)}", file=sys.stderr)
        return 1
    finding = build(comparison, assertions_by_id)
    if finding is None:
        print("NO_FINDING_CANDIDATE")
        return 0
    print(json.dumps(finding, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
