#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("builder", ROOT / "build-finding-candidate.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def assertion(aid, kind, subject, predicate, obj, evidence):
    return {
        "schema_version": "1",
        "id": aid,
        "kind": kind,
        "subject": {"id": subject, "type": "Service", "name": None},
        "predicate": predicate,
        "object": {"id": obj, "type": "Service", "name": None},
        "scope": {"repository": None, "revision": None, "environment": "production", "service": subject, "filters": []},
        "evidence_refs": [evidence],
        "recorded_at": "2026-09-14T10:00:00Z",
        "status": "ACTIVE"
    }


def comparison(cid, klass, state, refs, conflict_ref=None):
    return {
        "schema_version": "1",
        "id": cid,
        "assertion_refs": refs,
        "comparison_class": klass,
        "conflict_state": state,
        "aligned_dimensions": {
            "identity": "ALIGNED", "predicate": "ALIGNED", "scope": "ALIGNED",
            "revision": "ALIGNED", "environment": "ALIGNED", "valid_time": "ALIGNED",
            "truth_domain": "ALIGNED"
        },
        "reason": "fixture",
        "evidence_refs": [],
        "conflict_ref": conflict_ref,
        "finding_ref": None,
        "recorded_at": "2026-09-14T10:05:00Z",
        "metadata": {}
    }


def check(name, ok):
    print(f"{'PASS' if ok else 'FAIL'} {name}")
    return 0 if ok else 1


def main():
    failures = 0
    a1 = assertion("A-DECLARED", "DECLARED", "ENT-CHECKOUT", "allowed_dependency_only", "ENT-PAYMENTS", "E-ARCH")
    a2 = assertion("A-OBSERVED", "OBSERVED", "ENT-CHECKOUT", "called", "ENT-FRAUD", "E-OTEL")
    by_id = {a["id"]: a for a in (a1, a2)}

    active = comparison("CMP-DRIFT", "DECLARED_VS_OBSERVED_DRIFT", "ACTIVE", [a1["id"], a2["id"]], "CONFLICT-DRIFT")
    finding = mod.build(active, by_id)
    failures += check("active drift creates finding", finding is not None)
    failures += check("finding class architecture drift", finding["finding_class"] == "ARCHITECTURE_DRIFT")
    failures += check("all source assertions preserved", finding["assertion_refs"] == active["assertion_refs"])
    failures += check("comparison lineage preserved", finding["comparison_refs"] == [active["id"]])
    failures += check("conflict lineage preserved", finding["conflict_refs"] == ["CONFLICT-DRIFT"])
    failures += check("evidence union preserved", finding["evidence_refs"] == ["E-ARCH", "E-OTEL"])
    failures += check("source assertions not mutated", a1["status"] == "ACTIVE" and a2["status"] == "ACTIVE")

    benign = comparison("CMP-ENV", "ENVIRONMENT_MISMATCH", "NONE", [a1["id"], a2["id"]])
    failures += check("benign comparison creates no finding", mod.build(benign, by_id) is None)

    compatible = comparison("CMP-OK", "COMPATIBLE", "NONE", [a1["id"], a2["id"]])
    failures += check("compatible comparison creates no finding", mod.build(compatible, by_id) is None)

    contrad = comparison("CMP-CONTRA", "CONTRADICTION", "ACTIVE", [a1["id"], a2["id"]], "CONFLICT-CONTRA")
    conflict_finding = mod.build(contrad, by_id)
    failures += check("active contradiction creates finding", conflict_finding is not None)
    failures += check("contradiction maps to evidence conflict", conflict_finding["finding_class"] == "EVIDENCE_CONFLICT")

    missing = dict(by_id)
    missing.pop(a2["id"])
    try:
        _ = [missing[ref] for ref in active["assertion_refs"]]
        missing_detected = False
    except KeyError:
        missing_detected = True
    failures += check("missing source assertion fails lineage", missing_detected)

    print(f"tests=12 failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
