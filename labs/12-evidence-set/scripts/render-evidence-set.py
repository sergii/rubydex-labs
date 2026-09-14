#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def render(evidence_set):
    items = evidence_set["items"]
    lines = []

    lines.append("AUTHORITATIVE_EVIDENCE_SET")
    lines.append(f"target: {evidence_set['target']}")
    lines.append(f"count: {evidence_set['count']}")
    lines.append(f"complete: {str(evidence_set['complete']).lower()}")

    scope = evidence_set.get("scope") or {}
    lines.append("scope:")
    lines.append(f"  include: {json.dumps(scope.get('include', []), ensure_ascii=False, separators=(',', ':'))}")
    lines.append(f"  exclude: {json.dumps(scope.get('exclude', []), ensure_ascii=False, separators=(',', ':'))}")
    lines.append(f"  filters: {json.dumps(scope.get('filters', []), ensure_ascii=False, separators=(',', ':'))}")

    provenance = evidence_set["provenance"]
    lines.append("provenance:")
    for field in ("backend", "repository", "revision", "query_id", "observed_at"):
        lines.append(f"  {field}: {json.dumps(provenance.get(field), ensure_ascii=False, separators=(',', ':'))}")

    if evidence_set["complete"]:
        lines.append("membership_status: exhaustive_for_stated_scope")
    else:
        lines.append("membership_status: incomplete_do_not_infer_exhaustiveness")

    lines.append("items:")
    for item in items:
        # The stable key is always emitted verbatim and is the authoritative identity.
        payload = {
            "key": item["key"],
            "relation": item.get("relation"),
            "symbol": item.get("symbol"),
            "path": item.get("path"),
            "line": item.get("line"),
            "value": item.get("value"),
            "metadata": item.get("metadata", {}),
        }
        lines.append("  - " + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

    lines.append("END_AUTHORITATIVE_EVIDENCE_SET")
    return "\n".join(lines) + "\n"


def select_fixture(data, fixture_id):
    if isinstance(data, list):
        matches = [row for row in data if row.get("id") == fixture_id]
        if len(matches) != 1:
            raise SystemExit(f"fixture id must match exactly one row: {fixture_id}")
        return matches[0]["evidence_set"]
    return data


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: render-evidence-set.py <json> [fixture-id]", file=sys.stderr)
        return 2

    data = json.loads(Path(sys.argv[1]).read_text())
    if isinstance(data, list):
        if len(sys.argv) != 3:
            print("fixture-id is required when input is an array", file=sys.stderr)
            return 2
        evidence_set = select_fixture(data, sys.argv[2])
    else:
        evidence_set = data

    if evidence_set["count"] != len(evidence_set["items"]):
        print("refusing to render: count does not equal items.length", file=sys.stderr)
        return 1

    keys = [item["key"] for item in evidence_set["items"]]
    if len(keys) != len(set(keys)):
        print("refusing to render: duplicate item keys", file=sys.stderr)
        return 1

    sys.stdout.write(render(evidence_set))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
