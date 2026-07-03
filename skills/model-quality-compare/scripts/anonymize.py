#!/usr/bin/env python3
"""Anonymize model outputs for blinded judging.

Collects every trial output under <exp>/<model>/trial-*.*, shuffles them
deterministically, and copies them into <exp>/_judge/ as output_<LABEL>.<ext>.
Writes mapping.json (label -> model/trial/source) which MUST be withheld from
the judge subagent.
"""
import argparse
import json
import random
import shutil
import string
from pathlib import Path


def label_for(i: int) -> str:
    letters = string.ascii_uppercase
    if i < 26:
        return letters[i]
    return letters[i // 26 - 1] + letters[i % 26]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("exp_dir")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    exp = Path(args.exp_dir)
    outputs = []
    for model_dir in sorted(p for p in exp.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for f in sorted(model_dir.glob("trial-*.*")):
            if f.stat().st_size > 0:
                outputs.append((model_dir.name, f))
    if not outputs:
        raise SystemExit(f"No non-empty trial outputs found under {exp}")

    random.Random(args.seed).shuffle(outputs)

    judge_dir = exp / "_judge"
    judge_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}
    labels = []
    for i, (model, f) in enumerate(outputs):
        label = label_for(i)
        trial = f.stem.split("-")[-1]
        dest = judge_dir / f"output_{label}{f.suffix}"
        shutil.copyfile(f, dest)
        mapping[label] = {"model": model, "trial": trial, "source": str(f)}
        labels.append(label)

    (judge_dir / "mapping.json").write_text(json.dumps(mapping, indent=2))
    print(json.dumps({"labels": labels, "judge_dir": str(judge_dir)}, indent=2))


if __name__ == "__main__":
    main()
