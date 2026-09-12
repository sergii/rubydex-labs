#!/usr/bin/env python3
import json
import re
from pathlib import Path
import sys

if len(sys.argv) != 4:
    raise SystemExit("Usage: score-real-impact-pair.py PAIR_DIR ORDER GROUND_TRUTH_JSON")

pair_dir = Path(sys.argv[1])
order = sys.argv[2]
truth = json.loads(Path(sys.argv[3]).read_text())

SECTION_NAMES = [
    "Declaration",
    "Descendants",
    "Direct production references",
    "Plugin extensions",
    "Direct-reference spec files",
    "Read-first set",
]


def read_run(label):
    run_dir = Path((pair_dir / f"{label.lower()}-run-dir").read_text().strip())
    summary = json.loads((run_dir / "summary.json").read_text())
    final = (run_dir / "final.txt").read_text(errors="replace") if (run_dir / "final.txt").exists() else ""
    metadata = {}
    metadata_path = run_dir / "metadata.txt"
    if metadata_path.exists():
        for line in metadata_path.read_text().splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                metadata[key] = value
    return run_dir, summary, final, metadata


def split_sections(text):
    sections = {name: [] for name in SECTION_NAMES}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            heading = line[3:].strip()
            current = heading if heading in sections else None
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def clean_line(raw):
    line = raw.strip()
    if not line or line.startswith("```"):
        return ""
    if line.startswith(("- ", "* ")):
        line = line[2:].strip()
    if len(line) >= 2 and line[0] == "`" and line[-1] == "`":
        line = line[1:-1].strip()
    return line


def section_entries(lines):
    return [line for raw in lines if (line := clean_line(raw))]


def normalize_pair(line):
    if "|" not in line:
        return None
    left, right = line.split("|", 1)
    left = left.strip().strip("`")
    right = right.strip().strip("`")
    if not left or not re.fullmatch(r"[A-Za-z0-9_./-]+\.rb:\d+", right):
        return None
    return f"{left} | {right}"


def normalize_path_line(line):
    line = line.strip().strip("`")
    if re.fullmatch(r"[A-Za-z0-9_./-]+\.rb:\d+", line):
        return line
    return None


def normalize_rb_path(line):
    line = line.strip().strip("`")
    if re.fullmatch(r"[A-Za-z0-9_./-]+\.rb", line):
        return line
    return None


def score_set(actual, expected):
    actual = set(actual)
    expected = set(expected)
    tp = actual & expected
    fp = actual - expected
    missed = expected - actual
    precision = len(tp) / len(actual) if actual else 0.0
    recall = len(tp) / len(expected) if expected else 1.0
    return {
        "actual": sorted(actual),
        "true_positive": sorted(tp),
        "false_positive": sorted(fp),
        "missed": sorted(missed),
        "precision": precision,
        "recall": recall,
        "exact": not fp and not missed,
    }


def parse_and_score(final):
    sections = split_sections(final)

    declaration_entries = section_entries(sections["Declaration"])
    declaration = None
    for line in declaration_entries:
        candidate = normalize_path_line(line)
        if candidate:
            declaration = candidate
            break

    descendants = {
        value
        for line in section_entries(sections["Descendants"])
        if (value := normalize_pair(line))
    }
    production_refs = {
        value
        for line in section_entries(sections["Direct production references"])
        if (value := normalize_path_line(line))
    }
    plugin_extensions = {
        value
        for line in section_entries(sections["Plugin extensions"])
        if (value := normalize_pair(line))
    }
    spec_files = {
        value
        for line in section_entries(sections["Direct-reference spec files"])
        if (value := normalize_rb_path(line))
    }

    read_first = []
    malformed_read_first = []
    for line in section_entries(sections["Read-first set"]):
        if "|" not in line:
            malformed_read_first.append(line)
            continue
        path, reason = line.split("|", 1)
        path = path.strip().strip("`")
        reason = reason.strip()
        if not normalize_rb_path(path):
            malformed_read_first.append(line)
            continue
        read_first.append({"path": path, "reason": reason})

    read_paths = {entry["path"] for entry in read_first}
    rubric = truth["read_first_rubric"]
    category_results = {}
    for name, candidates in rubric["categories"].items():
        matched = sorted(read_paths & set(candidates))
        category_results[name] = {
            "covered": bool(matched),
            "matched": matched,
        }
    covered_count = sum(1 for value in category_results.values() if value["covered"])
    reasons_complete = bool(read_first) and all(entry["reason"] for entry in read_first)

    descendant_score = score_set(descendants, truth["named_descendants"])
    production_score = score_set(production_refs, truth["direct_production_references"])
    plugin_score = score_set(plugin_extensions, truth["plugin_extensions"])
    spec_score = score_set(spec_files, truth["direct_reference_spec_files"])

    return {
        "declaration": {
            "actual": declaration,
            "expected": truth["declaration"],
            "exact": declaration == truth["declaration"],
        },
        "descendants": descendant_score,
        "direct_production_references": production_score,
        "plugin_extensions": plugin_score,
        "direct_reference_spec_files": spec_score,
        "structural_exact": (
            declaration == truth["declaration"]
            and descendant_score["exact"]
            and production_score["exact"]
            and plugin_score["exact"]
            and spec_score["exact"]
        ),
        "read_first": {
            "files": read_first,
            "malformed": malformed_read_first,
            "size": len(read_first),
            "max_files": rubric["max_files"],
            "within_limit": len(read_first) <= rubric["max_files"],
            "reasons_complete": reasons_complete,
            "category_results": category_results,
            "coverage": covered_count,
            "coverage_total": len(category_results),
        },
    }


a_dir, a_summary, a_final, a_meta = read_run("A")
b_dir, b_summary, b_final, b_meta = read_run("B")
a_score = parse_and_score(a_final)
b_score = parse_and_score(b_final)

metrics = [
    ("elapsed_seconds", lambda s: s["elapsed_seconds"]),
    ("total_tokens", lambda s: s["usage"]["total_tokens"]),
    ("input_tokens", lambda s: s["usage"]["input_tokens"]),
    ("cached_input_tokens", lambda s: s["usage"]["cached_input_tokens"]),
    ("uncached_input_tokens", lambda s: s["usage"]["uncached_input_tokens"]),
    ("output_tokens", lambda s: s["usage"]["output_tokens"]),
    ("reasoning_output_tokens", lambda s: s["usage"]["reasoning_output_tokens"]),
]

comparison = {
    "repository": truth["repository"],
    "revision": truth["revision"],
    "target": truth["target"],
    "order": order,
    "model": a_meta.get("model"),
    "reasoning": a_meta.get("reasoning"),
    "a_run_dir": str(a_dir),
    "b_run_dir": str(b_dir),
    "a_score": a_score,
    "b_score": b_score,
    "metrics": {},
    "scoring": "section_aware_impact_v1",
}

rows = []
for name, getter in metrics:
    av = int(getter(a_summary))
    bv = int(getter(b_summary))
    delta = bv - av
    pct = (delta / av * 100.0) if av else None
    pct_text = "n/a" if pct is None else f"{pct:+.1f}%"
    comparison["metrics"][name] = {"a": av, "b": bv, "delta": delta, "percent": pct}
    rows.append((name, av, bv, pct_text))

(pair_dir / "comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")


def structural_table_row(label, key):
    aa = a_score[key]
    bb = b_score[key]
    return (
        f"| {label} | "
        f"{len(aa['true_positive'])}/{len(aa['true_positive']) + len(aa['missed'])}, FP {len(aa['false_positive'])} | "
        f"{len(bb['true_positive'])}/{len(bb['true_positive']) + len(bb['missed'])}, FP {len(bb['false_positive'])} |"
    )

model = comparison["model"] or "unknown"
reasoning = comparison["reasoning"] or "unknown"
lines = [
    "# Real Discourse impact-map comparison",
    "",
    f"Repository: `{truth['repository']}`",
    f"Revision: `{truth['revision']}`",
    f"Target: `{truth['target']}`",
    f"Model: `{model}`",
    f"Reasoning: `{reasoning}`",
    f"Execution order: `{order}`",
    "Scoring: section-aware impact-map scorer v1",
    "",
    "## Structural correctness",
    "",
    "| Set | A - text | B - Rubydex |",
    "| --- | ---: | ---: |",
    f"| Declaration exact | {'yes' if a_score['declaration']['exact'] else 'no'} | {'yes' if b_score['declaration']['exact'] else 'no'} |",
    structural_table_row("Named descendants", "descendants"),
    structural_table_row("Direct production refs", "direct_production_references"),
    structural_table_row("Plugin extensions", "plugin_extensions"),
    structural_table_row("Direct-reference spec files", "direct_reference_spec_files"),
    f"| All structural sets exact | {'yes' if a_score['structural_exact'] else 'no'} | {'yes' if b_score['structural_exact'] else 'no'} |",
    "",
    "## Read-first quality",
    "",
    "| Metric | A - text | B - Rubydex |",
    "| --- | ---: | ---: |",
    f"| Coverage categories | {a_score['read_first']['coverage']}/{a_score['read_first']['coverage_total']} | {b_score['read_first']['coverage']}/{b_score['read_first']['coverage_total']} |",
    f"| Files selected | {a_score['read_first']['size']} | {b_score['read_first']['size']} |",
    f"| Within 12-file limit | {'yes' if a_score['read_first']['within_limit'] else 'no'} | {'yes' if b_score['read_first']['within_limit'] else 'no'} |",
    f"| Every entry has reason | {'yes' if a_score['read_first']['reasons_complete'] else 'no'} | {'yes' if b_score['read_first']['reasons_complete'] else 'no'} |",
    "",
    "## Cost and latency",
    "",
    "| Metric | A - text | B - Rubydex | B vs A |",
    "| --- | ---: | ---: | ---: |",
]
for name, av, bv, pct_text in rows:
    lines.append(f"| {name} | {av:,} | {bv:,} | {pct_text} |")

for label, score in (("A", a_score), ("B", b_score)):
    for title, key in (
        ("Named descendants", "descendants"),
        ("Direct production references", "direct_production_references"),
        ("Plugin extensions", "plugin_extensions"),
        ("Direct-reference spec files", "direct_reference_spec_files"),
    ):
        data = score[key]
        if data["missed"] or data["false_positive"]:
            lines.extend(["", f"### {label} - {title} differences"])
            if data["missed"]:
                lines.extend(["", "Missed:", "", "```text", *data["missed"], "```"])
            if data["false_positive"]:
                lines.extend(["", "False positives:", "", "```text", *data["false_positive"], "```"])

lines.extend([
    "",
    "## A final answer",
    "",
    a_final.rstrip(),
    "",
    "## B final answer",
    "",
    b_final.rstrip(),
    "",
])
(pair_dir / "comparison.md").write_text("\n".join(lines))

summary_lines = [
    "status: completed",
    f"repository: {truth['repository']}",
    f"revision: {truth['revision']}",
    f"target: {truth['target']}",
    f"order: {order}",
    f"model: {model}",
    f"reasoning: {reasoning}",
    "scoring: section_aware_impact_v1",
    f"structural_exact_a: {'yes' if a_score['structural_exact'] else 'no'}",
    f"structural_exact_b: {'yes' if b_score['structural_exact'] else 'no'}",
    f"descendants_a: {len(a_score['descendants']['true_positive'])}/{len(truth['named_descendants'])} fp={len(a_score['descendants']['false_positive'])}",
    f"descendants_b: {len(b_score['descendants']['true_positive'])}/{len(truth['named_descendants'])} fp={len(b_score['descendants']['false_positive'])}",
    f"production_refs_a: {len(a_score['direct_production_references']['true_positive'])}/{len(truth['direct_production_references'])} fp={len(a_score['direct_production_references']['false_positive'])}",
    f"production_refs_b: {len(b_score['direct_production_references']['true_positive'])}/{len(truth['direct_production_references'])} fp={len(b_score['direct_production_references']['false_positive'])}",
    f"plugin_extensions_a: {len(a_score['plugin_extensions']['true_positive'])}/{len(truth['plugin_extensions'])} fp={len(a_score['plugin_extensions']['false_positive'])}",
    f"plugin_extensions_b: {len(b_score['plugin_extensions']['true_positive'])}/{len(truth['plugin_extensions'])} fp={len(b_score['plugin_extensions']['false_positive'])}",
    f"spec_files_a: {len(a_score['direct_reference_spec_files']['true_positive'])}/{len(truth['direct_reference_spec_files'])} fp={len(a_score['direct_reference_spec_files']['false_positive'])}",
    f"spec_files_b: {len(b_score['direct_reference_spec_files']['true_positive'])}/{len(truth['direct_reference_spec_files'])} fp={len(b_score['direct_reference_spec_files']['false_positive'])}",
    f"read_first_coverage_a: {a_score['read_first']['coverage']}/{a_score['read_first']['coverage_total']}",
    f"read_first_coverage_b: {b_score['read_first']['coverage']}/{b_score['read_first']['coverage_total']}",
    f"read_first_size_a: {a_score['read_first']['size']}",
    f"read_first_size_b: {b_score['read_first']['size']}",
]
for name, av, bv, pct_text in rows:
    summary_lines.append(f"{name}: A={av} B={bv} B_vs_A={pct_text}")
(pair_dir / "summary.txt").write_text("\n".join(summary_lines) + "\n")
