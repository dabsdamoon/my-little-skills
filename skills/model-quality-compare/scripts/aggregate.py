#!/usr/bin/env python3
"""De-anonymize judge scores and merge objective results into a scorecard report.

Reads (all optional):
  <exp>/_judge/mapping.json   label -> {model, trial}
  <exp>/_judge/scores.json    label -> {dimension: score, ...}   (written by judge subagent)
  <exp>/objective.json        [{model, trial, passed, detail}]   (written by orchestrator)
Writes <exp>/report.md
"""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("exp_dir")
    args = ap.parse_args()
    exp = Path(args.exp_dir)

    mapping = load(exp / "_judge" / "mapping.json") or {}
    scores = load(exp / "_judge" / "scores.json") or {}
    objective = load(exp / "objective.json") or []

    lines = ["# Model Quality Comparison Report", ""]

    if objective:
        agg = defaultdict(lambda: {"pass": 0, "total": 0})
        for r in objective:
            a = agg[r["model"]]
            a["total"] += 1
            a["pass"] += 1 if r.get("passed") else 0
        lines += ["## Objective results", "", "| Model | Pass rate | Trials |", "|---|---|---|"]
        for model in sorted(agg):
            a = agg[model]
            rate = a["pass"] / a["total"] if a["total"] else 0
            lines.append(f"| {model} | {a['pass']}/{a['total']} ({rate:.0%}) | {a['total']} |")
        lines += ["", "<details><summary>Per-trial detail</summary>", "",
                  "| Model | Trial | Passed | Detail |", "|---|---|---|---|"]
        for r in sorted(objective, key=lambda r: (r["model"], str(r["trial"]))):
            passed = "PASS" if r.get("passed") else "FAIL"
            lines.append(f"| {r['model']} | {r['trial']} | {passed} | {r.get('detail', '')} |")
        lines += ["", "</details>", ""]

    if scores and mapping:
        dims = set()
        per_model = defaultdict(lambda: defaultdict(list))
        for label, dimscores in scores.items():
            info = mapping.get(label)
            if not info:
                continue
            for d, v in dimscores.items():
                if isinstance(v, (int, float)):
                    per_model[info["model"]][d].append(v)
                    dims.add(d)
        dims = sorted(dims)
        lines += ["## Blinded judge scores", "",
                  "| Model | " + " | ".join(f"{d} (mean+-sd)" for d in dims) + " | overall |",
                  "|" + "---|" * (len(dims) + 2)]
        for model in sorted(per_model):
            cells, all_vals = [], []
            for d in dims:
                vals = per_model[model].get(d, [])
                if vals:
                    sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
                    cells.append(f"{statistics.mean(vals):.2f}+-{sd:.2f}")
                    all_vals += vals
                else:
                    cells.append("-")
            overall = f"{statistics.mean(all_vals):.2f}" if all_vals else "-"
            lines.append(f"| {model} | " + " | ".join(cells) + f" | {overall} |")
        lines += ["", "> Judge scores are model opinion, not ground truth.", ""]

    lines += ["## Caveats", "",
              "- Non-determinism: outputs vary run to run; gaps smaller than the spread are noise.",
              "- Judge is a single model; if it is also a contestant, self-preference may inflate its own score.",
              "- Objective checks are ground truth; judge scores are opinion.", ""]

    (exp / "report.md").write_text("\n".join(lines))
    print(f"Wrote {exp / 'report.md'}")


if __name__ == "__main__":
    main()
