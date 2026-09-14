#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load_fixture(path, fixture_id):
    rows = json.loads(Path(path).read_text())
    for row in rows:
        if row.get("id") == fixture_id:
            return row
    raise SystemExit(f"unknown fixture: {fixture_id}")


def parse_rendered(path):
    keys = []
    count = None
    complete = None
    membership_status = None
    scope = {}
    provenance = {}
    section = None
    started = False
    ended = False

    for line in Path(path).read_text().splitlines():
        if line == "AUTHORITATIVE_EVIDENCE_SET":
            started = True
            continue
        if line == "END_AUTHORITATIVE_EVIDENCE_SET":
            ended = True
            continue
        if line == "scope:":
            section = "scope"
            continue
        if line == "provenance:":
            section = "provenance"
            continue
        if line == "items:":
            section = "items"
            continue
        if line.startswith("count: "):
            count = int(line.split(": ", 1)[1])
            section = None
            continue
        if line.startswith("complete: "):
            complete = line.split(": ", 1)[1] == "true"
            section = None
            continue
        if line.startswith("membership_status: "):
            membership_status = line.split(": ", 1)[1]
            section = None
            continue
        if section == "items" and line.startswith("  - "):
            item = json.loads(line[4:])
            keys.append(item["key"])
            continue
        if section in ("scope", "provenance") and line.startswith("  "):
            key, raw = line.strip().split(": ", 1)
            value = json.loads(raw)
            if section == "scope":
                scope[key] = value
            else:
                provenance[key] = value

    return {
        "keys": keys,
        "count": count,
        "complete": complete,
        "membership_status": membership_status,
        "scope": scope,
        "provenance": provenance,
        "started": started,
        "ended": ended,
    }


def main():
    if len(sys.argv) != 4:
        print("usage: score-rendering.py <fixtures.json> <fixture-id> <rendered.txt>", file=sys.stderr)
        return 2

    fixture = load_fixture(sys.argv[1], sys.argv[2])
    evidence_set = fixture["evidence_set"]
    rendered = parse_rendered(sys.argv[3])

    expected_keys = [item["key"] for item in evidence_set["items"]]
    expected_key_set = set(expected_keys)
    rendered_key_set = set(rendered["keys"])

    if expected_key_set:
        recall = len(expected_key_set & rendered_key_set) / len(expected_key_set)
    else:
        recall = 1.0 if not rendered_key_set else 0.0

    if rendered_key_set:
        precision = len(expected_key_set & rendered_key_set) / len(rendered_key_set)
    else:
        precision = 1.0 if not expected_key_set else 0.0

    expected_scope = evidence_set.get("scope") or {}
    expected_scope = {
        "include": expected_scope.get("include", []),
        "exclude": expected_scope.get("exclude", []),
        "filters": expected_scope.get("filters", []),
    }

    source_provenance = evidence_set["provenance"]
    expected_provenance = {
        name: source_provenance.get(name)
        for name in ("backend", "repository", "revision", "query_id", "observed_at")
    }

    expected_status = (
        "exhaustive_for_stated_scope"
        if evidence_set["complete"]
        else "incomplete_do_not_infer_exhaustiveness"
    )

    checks = {
        "exact_membership": rendered["keys"] == expected_keys,
        "count_ok": rendered["count"] == evidence_set["count"] == len(rendered["keys"]),
        "complete_flag_ok": rendered["complete"] == evidence_set["complete"],
        "completeness_claim_ok": rendered["membership_status"] == expected_status,
        "scope_ok": rendered["scope"] == expected_scope,
        "provenance_ok": rendered["provenance"] == expected_provenance,
        "framing_ok": rendered["started"] and rendered["ended"],
    }
    passed = all(checks.values())

    result = {
        "fixture_id": fixture["id"],
        "pass": passed,
        "recall": recall,
        "precision": precision,
        "omissions": [key for key in expected_keys if key not in rendered_key_set],
        "additions": [key for key in rendered["keys"] if key not in expected_key_set],
        **checks,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
