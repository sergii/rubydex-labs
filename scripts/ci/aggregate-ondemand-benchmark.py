#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re, statistics, zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

CONDITIONS = ("D", "E")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.+-]+Z?)")
PRICING = {"gpt-5.6-luna": {"input": 0.20, "cached": 0.02, "output": 1.20}}


def split_sections(text):
    out, current = {}, None
    for raw in text.splitlines():
        if raw.startswith("## "):
            current = raw[3:].strip(); out.setdefault(current, [])
        elif current:
            out[current].append(raw)
    return out


def ids(lines, prefix):
    result = set(); pattern = re.compile(rf"({re.escape(prefix)}[A-Z0-9-]+)")
    for raw in lines:
        line = raw.strip().lstrip("-* ").strip("`")
        match = pattern.match(line)
        if match: result.add(match.group(1))
    return result


def score_set(actual, expected):
    tp = actual & expected
    return {
        "precision": len(tp) / len(actual) if actual else 0.0,
        "recall": len(tp) / len(expected) if expected else 1.0,
        "exact": actual == expected,
        "false_positive": sorted(actual - expected),
        "missed": sorted(expected - actual),
    }


def score_final(text, truth):
    s = split_sections(text)
    impacts = score_set(ids(s.get("Impacts", []), "IMPACT-"), set(truth["impacts"]))
    risks = score_set(ids(s.get("Risks", []), "RISK-"), set(truth["risks"]))
    verification = score_set(ids(s.get("Verification", []), "VERIFY-"), set(truth["verification"]))
    policies = score_set(ids(s.get("Policy violations", []), "POLICY-"), set(truth["policy_violations"]))
    recommendation_text = "\n".join(s.get("Recommendation", []))
    recommendation = next((x for x in ("SAFE", "CAUTION", "BLOCK") if re.search(rf"\b{x}\b", recommendation_text)), None)
    return {
        "impacts": impacts, "risks": risks, "verification": verification, "policies": policies,
        "recommendation": recommendation,
        "consequence_exact": impacts["exact"] and risks["exact"] and verification["exact"],
        "knowledge_exact": policies["exact"] and recommendation == truth["recommendation"],
    }


def decode(path):
    data = path.read_bytes()
    if data.startswith(b"PK"):
        with zipfile.ZipFile(BytesIO(data)) as z:
            return "\n".join(z.read(n).decode("utf-8", "replace") for n in z.namelist() if not n.endswith("/"))
    return data.decode("utf-8", "replace")


def ts(line):
    m = TIMESTAMP_RE.match(line)
    if not m: return None
    value = m.group(1)
    if value.endswith("Z"): value = value[:-1] + "+00:00"
    try: return datetime.fromisoformat(value)
    except ValueError: return None


def event(line):
    clean = ANSI_RE.sub("", line); i = clean.find("{")
    if i < 0: return None
    try:
        value, _ = json.JSONDecoder().raw_decode(clean[i:].strip())
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def metrics(path):
    if not path.exists(): return {}
    start = first = end = None; usage = {}
    for line in decode(path).splitlines():
        timestamp = ts(line)
        if start is None and "Running:" in line and " exec " in line: start = timestamp
        e = event(line)
        if not e: continue
        if first is None: first = timestamp
        if e.get("type") == "turn.completed": usage = e.get("usage") or {}; end = timestamp
    inp = int(usage.get("input_tokens") or 0); cached = int(usage.get("cached_input_tokens") or 0)
    out = int(usage.get("output_tokens") or 0); total = int(usage.get("total_tokens") or inp + out)
    begun = start or first
    return {
        "elapsed_seconds": max((end - begun).total_seconds(), 0.0) if begun and end else None,
        "input_tokens": inp, "cached_input_tokens": cached, "uncached_input_tokens": max(inp-cached,0),
        "output_tokens": out, "total_tokens": total,
    }


def cost(model, m):
    p = PRICING.get(model)
    if not p or not m.get("total_tokens"): return None
    return (m["uncached_input_tokens"]*p["input"] + m["cached_input_tokens"]*p["cached"] + m["output_tokens"]*p["output"]) / 1_000_000


def med(samples, key):
    vals = [s["metrics"].get(key) for s in samples if s["metrics"].get(key) is not None]
    return statistics.median(vals) if vals else None


def medscore(samples, section, key):
    vals = [s["score"][section][key] for s in samples]
    return statistics.median(vals) if vals else 0.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--artifacts", required=True); ap.add_argument("--logs", required=True); ap.add_argument("--output", required=True)
    args = ap.parse_args(); root = Path(__file__).resolve().parents[2]
    truth = json.loads((root / "labs/07-rubydex-on-demand/ground-truth.json").read_text())
    samples = []
    for meta_path in sorted(Path(args.artifacts).glob("sample-*/meta.json")):
        meta = json.loads(meta_path.read_text()); condition = meta["condition"]; repeat = int(meta["repeat"]); job = f"sample-{condition}-r{repeat}"
        final_path = meta_path.parent / "final.txt"; final = final_path.read_text(errors="replace") if final_path.exists() else ""
        m = metrics(Path(args.logs) / f"{job}.log"); m["estimated_cost_usd"] = cost(args.model, m)
        samples.append({"job": job, "meta": meta, "metrics": m, "score": score_final(final, truth)})
    grouped = {c:[s for s in samples if s["meta"]["condition"]==c] for c in CONDITIONS}
    outdir = Path(args.output); outdir.mkdir(parents=True, exist_ok=True)
    result = {"lab":"07","model":args.model,"samples":samples}
    (outdir/"report.json").write_text(json.dumps(result, indent=2)+"\n")
    lines = ["# Lab 07 - Rubydex on-demand benchmark","",f"- Model: `{args.model}`",f"- Samples: D={len(grouped['D'])}, E={len(grouped['E'])}","",
             "## Median correctness","","| Condition | Impact recall | Risk recall | Verification recall | Policy recall | Consequence exact | Knowledge exact |","| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for c in CONDITIONS:
        ss=grouped[c]
        lines.append(f"| {c} | {medscore(ss,'impacts','recall'):.1%} | {medscore(ss,'risks','recall'):.1%} | {medscore(ss,'verification','recall'):.1%} | {medscore(ss,'policies','recall'):.1%} | {sum(s['score']['consequence_exact'] for s in ss)}/{len(ss)} | {sum(s['score']['knowledge_exact'] for s in ss)}/{len(ss)} |")
    lines += ["","## Median efficiency","","| Metric | D - knowledge | E - knowledge + Rubydex available |","| --- | ---: | ---: |"]
    for key,label in [("elapsed_seconds","elapsed seconds"),("total_tokens","total tokens"),("uncached_input_tokens","uncached input"),("output_tokens","output tokens"),("estimated_cost_usd","estimated API cost")]:
        vals=[]
        for c in CONDITIONS:
            v=med(grouped[c],key)
            vals.append("n/a" if v is None else (f"${v:.4f}" if key=="estimated_cost_usd" else (f"{v:.1f}" if key=="elapsed_seconds" else f"{v:,.0f}")))
        lines.append(f"| {label} | {vals[0]} | {vals[1]} |")
    lines += ["","## Interpretation guardrails","","- D and E receive identical source, architecture knowledge, skill, model, reasoning effort, and output vocabulary.","- E merely has Rubydex MCP available; the prompt does not require or mention using it.","- The fixture intentionally contains inheritance, aliasing, a reopened class, and lexical decoys.","- A win for E is meaningful only if correctness improves enough to justify any added tool/token cost.",""]
    (outdir/"report.md").write_text("\n".join(lines)); print("\n".join(lines))

if __name__ == "__main__": main()
