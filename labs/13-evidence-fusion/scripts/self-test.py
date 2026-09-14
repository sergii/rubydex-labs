#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPARE_PATH = ROOT / "compare-assertions.py"
RULES_PATH = ROOT.parent / "fixtures" / "predicate-rules.json"

spec = importlib.util.spec_from_file_location("lab13_compare", COMPARE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
rules = mod.load_rules(RULES_PATH)


def entity(entity_id, name="svc"):
    return {"id": entity_id, "type": "Service", "name": name}


def scalar(value):
    return {"value": value}


def assertion(assertion_id, predicate, obj, *, subject="ENT-A", environment="production", revision="rev-1", valid_from="2026-09-14T00:00:00Z", valid_to="2026-09-14T01:00:00Z", kind="OBSERVED"):
    return {
        "schema_version": "1",
        "id": assertion_id,
        "kind": kind,
        "subject": entity(subject, "payments-api"),
        "predicate": predicate,
        "object": obj,
        "scope": {
            "repository": "example/repo",
            "revision": revision,
            "environment": environment,
            "service": "payments-api",
            "filters": [],
        },
        "valid_time": {"from": valid_from, "to": valid_to},
        "evidence_refs": [f"EV-{assertion_id}"],
        "recorded_at": "2026-09-14T01:05:00Z",
        "status": "ACTIVE",
    }


def check(name, expected, left, right):
    actual = mod.classify(left, right, rules)
    ok = actual == expected
    print(f"{'PASS' if ok else 'FAIL'} {name} expected={expected} actual={actual}")
    return ok


def main():
    base_left = assertion("L", "configured_value", scalar("on"))
    base_right = assertion("R", "configured_value", scalar("off"))

    tests = []
    tests.append(("true-contradiction-baseline", "CONTRADICTION", base_left, base_right))

    r = copy.deepcopy(base_right)
    r["scope"]["environment"] = "staging"
    tests.append(("environment-mismatch-not-contradiction", "ENVIRONMENT_MISMATCH", base_left, r))

    r = copy.deepcopy(base_right)
    r["scope"]["revision"] = "rev-2"
    tests.append(("revision-mismatch-not-contradiction", "REVISION_MISMATCH", base_left, r))

    r = copy.deepcopy(base_right)
    r["valid_time"] = {"from": "2026-09-14T02:00:00Z", "to": "2026-09-14T03:00:00Z"}
    tests.append(("time-mismatch-not-contradiction", "TEMPORAL_MISMATCH", base_left, r))

    r = copy.deepcopy(base_right)
    r["subject"]["id"] = "ENT-B"
    r["subject"]["name"] = base_left["subject"]["name"]
    tests.append(("same-name-different-id-not-contradiction", "IDENTITY_UNRESOLVED", base_left, r))

    semantic = assertion("S", "references", entity("ENT-B", "ledger-api"), kind="DETERMINISTIC")
    runtime = assertion("O", "called", entity("ENT-B", "ledger-api"), kind="OBSERVED")
    tests.append(("different-truth-domain-compatible", "COMPATIBLE", semantic, runtime))

    noncomp = copy.deepcopy(runtime)
    noncomp["predicate"] = "owned_by"
    tests.append(("non-comparable-predicate-not-contradiction", "NON_COMPARABLE_PREDICATE", semantic, noncomp))

    declared = assertion("D", "allowed_dependency_only", entity("ENT-B", "payments-v2"), kind="DECLARED")
    observed = assertion("O2", "called", entity("ENT-C", "legacy-payments"), kind="OBSERVED")
    tests.append(("declared-vs-observed-drift", "DECLARED_VS_OBSERVED_DRIFT", declared, observed))

    observed_env = copy.deepcopy(observed)
    observed_env["scope"]["environment"] = "staging"
    tests.append(("drift-with-environment-mismatch", "ENVIRONMENT_MISMATCH", declared, observed_env))

    observed_rev = copy.deepcopy(observed)
    observed_rev["scope"]["revision"] = "rev-2"
    tests.append(("drift-with-revision-mismatch", "REVISION_MISMATCH", declared, observed_rev))

    failures = 0
    for name, expected, left, right in tests:
        if not check(name, expected, left, right):
            failures += 1

    print(f"tests={len(tests)} failures={failures}")
    if failures == 0:
        print("LAB13_FALSE_CONFLICT_SELF_TEST_PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
