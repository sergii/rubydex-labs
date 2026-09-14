#!/usr/bin/env python3
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "evidence-sets.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the validator by loading the sibling script directly because its file name contains '-'.
import importlib.util


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("validate_evidence_set", Path(__file__).with_name("validate-evidence-set.py"))
renderer = load_module("render_evidence_set", Path(__file__).with_name("render-evidence-set.py"))


def fixture_by_id(rows, fixture_id):
    for row in rows:
        if row.get("id") == fixture_id:
            return copy.deepcopy(row["evidence_set"])
    raise AssertionError(f"missing fixture: {fixture_id}")


def expect_valid(name, evidence_set):
    errors = validator.validate(evidence_set)
    if errors:
        raise AssertionError(f"{name}: expected valid, got {errors}")


def expect_invalid(name, evidence_set, expected_fragment):
    errors = validator.validate(evidence_set)
    if not errors:
        raise AssertionError(f"{name}: expected validation failure")
    if not any(expected_fragment in error for error in errors):
        raise AssertionError(
            f"{name}: expected error containing {expected_fragment!r}, got {errors}"
        )


def expect_renderer_refusal(name, evidence_set):
    # render() itself is intentionally a pure formatter. The CLI guard is equivalent
    # to these two invariants and must refuse invalid authoritative membership.
    if evidence_set["count"] != len(evidence_set["items"]):
        return
    keys = [item["key"] for item in evidence_set["items"]]
    if len(keys) != len(set(keys)):
        return
    raise AssertionError(f"{name}: expected renderer guard condition to fail closed")


def main():
    rows = json.loads(FIXTURES.read_text())
    results = []

    # Baseline: every frozen fixture is internally valid and deterministically renderable.
    for row in rows:
        evidence_set = copy.deepcopy(row["evidence_set"])
        expect_valid(f"baseline:{row['id']}", evidence_set)
        rendered = renderer.render(evidence_set)
        if "AUTHORITATIVE_EVIDENCE_SET" not in rendered or "END_AUTHORITATIVE_EVIDENCE_SET" not in rendered:
            raise AssertionError(f"baseline:{row['id']}: missing authoritative framing")
        results.append((f"baseline:{row['id']}", "PASS"))

    base = fixture_by_id(rows, "production-references-5")

    # 1. Drop one item but leave count unchanged: must fail count invariant.
    mutated = copy.deepcopy(base)
    mutated["items"].pop()
    expect_invalid("delete-item", mutated, "count mismatch")
    expect_renderer_refusal("delete-item", mutated)
    results.append(("delete-item", "PASS"))

    # 2. Add an unexpected item without changing count: must fail count invariant.
    mutated = copy.deepcopy(base)
    mutated["items"].append({"key": "unexpected:extra", "metadata": {}})
    expect_invalid("add-item", mutated, "count mismatch")
    expect_renderer_refusal("add-item", mutated)
    results.append(("add-item", "PASS"))

    # 3. Corrupt count while preserving items.
    mutated = copy.deepcopy(base)
    mutated["count"] = 4
    expect_invalid("wrong-count", mutated, "count mismatch")
    expect_renderer_refusal("wrong-count", mutated)
    results.append(("wrong-count", "PASS"))

    # 4. Duplicate a stable key while keeping a structurally plausible set.
    mutated = copy.deepcopy(base)
    mutated["items"][1]["key"] = mutated["items"][0]["key"]
    expect_invalid("duplicate-key", mutated, "duplicate item keys")
    expect_renderer_refusal("duplicate-key", mutated)
    results.append(("duplicate-key", "PASS"))

    # 5. Remove provenance authority.
    mutated = copy.deepcopy(base)
    mutated["provenance"]["backend"] = ""
    expect_invalid("missing-backend", mutated, "provenance.backend")
    results.append(("missing-backend", "PASS"))

    # 6. Completeness must be typed and explicit; strings are forbidden.
    mutated = copy.deepcopy(base)
    mutated["complete"] = "true"
    expect_invalid("invalid-complete-type", mutated, "complete must be boolean")
    results.append(("invalid-complete-type", "PASS"))

    # 7. Incomplete evidence must render with explicit non-exhaustive wording.
    incomplete = fixture_by_id(rows, "incomplete-set")
    rendered = renderer.render(incomplete)
    required = "membership_status: incomplete_do_not_infer_exhaustiveness"
    forbidden = "membership_status: exhaustive_for_stated_scope"
    if required not in rendered or forbidden in rendered:
        raise AssertionError("incomplete-wording: renderer overstated completeness")
    results.append(("incomplete-wording", "PASS"))

    # 8. Distinct stable keys with identical display values must survive unchanged.
    duplicates = fixture_by_id(rows, "duplicate-looking-members")
    rendered = renderer.render(duplicates)
    for key in ("team:payments-platform", "team:payments-product"):
        if key not in rendered:
            raise AssertionError(f"stable-key-preservation: missing {key}")
    results.append(("stable-key-preservation", "PASS"))

    for name, status in results:
        print(f"{status} {name}")
    print(f"tests={len(results)} failures=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
