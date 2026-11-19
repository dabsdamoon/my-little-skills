#!/usr/bin/env python3
"""API-backed, version-pinned contestant runner.

Use this instead of subagent fan-out when the comparison needs SPECIFIC model
versions (e.g. claude-sonnet-4-6 vs claude-sonnet-5) that the Claude Code
subagent aliases (opus/sonnet/haiku/fable) cannot address. Calls the Anthropic
API directly with pinned model IDs, so it spends metered API tokens, not the
subscription. Requires ANTHROPIC_API_KEY in the environment.

Reads <exp>/api_spec.json:
  {
    "models": [{"name": "sonnet46", "id": "claude-sonnet-4-6"}, ...],
    "trials": 1,
    "frozen_prompt": "....",
    "output_ext": "py",
    "max_tokens": 1024
  }
Writes each output to <exp>/<name>/trial-<n>.<ext> (same layout the objective
check, anonymize.py, and aggregate.py expect) plus <exp>/runs.json (latency +
token usage per run — secondary metrics).
"""
import argparse
import json
import time
from pathlib import Path

import anthropic


def strip_fences(text: str) -> str:
    """Drop a leading ```lang / trailing ``` fence if the model wrapped its code."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        lines = lines[1:]  # drop ```lang
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t + "\n"


def call(client, model_id: str, prompt: str, max_tokens: int):
    """Call the model with thinking disabled for a fair comparison; fall back if rejected."""
    kwargs = dict(model=model_id, max_tokens=max_tokens,
                  messages=[{"role": "user", "content": prompt}])
    try:
        return client.messages.create(thinking={"type": "disabled"}, **kwargs)
    except anthropic.BadRequestError:
        return client.messages.create(**kwargs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("exp_dir")
    args = ap.parse_args()
    exp = Path(args.exp_dir)
    spec = json.loads((exp / "api_spec.json").read_text())

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    ext = spec.get("output_ext", "txt")
    max_tokens = spec.get("max_tokens", 1024)
    trials = spec.get("trials", 1)

    runs = []
    for m in spec["models"]:
        name, model_id = m["name"], m["id"]
        outdir = exp / name
        outdir.mkdir(parents=True, exist_ok=True)
        for t in range(1, trials + 1):
            dest = outdir / f"trial-{t}.{ext}"
            t0 = time.monotonic()
            try:
                resp = call(client, model_id, spec["frozen_prompt"], max_tokens)
            except Exception as e:
                dest.write_text("")  # empty output = recorded failure for this model
                runs.append({"model": name, "model_id": model_id, "trial": t, "error": str(e)})
                print(f"{name} trial {t}: ERROR {e}")
                continue
            dt = time.monotonic() - t0
            text = "".join(b.text for b in resp.content if b.type == "text")
            dest.write_text(strip_fences(text) if ext == "py" else text)
            u = resp.usage
            runs.append({"model": name, "model_id": model_id, "trial": t,
                         "latency_s": round(dt, 2),
                         "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                         "stop_reason": resp.stop_reason})
            print(f"{name} trial {t}: {dt:.1f}s, out={u.output_tokens}tok, stop={resp.stop_reason}")

    (exp / "runs.json").write_text(json.dumps(runs, indent=2))
    print(f"wrote {exp / 'runs.json'}")


if __name__ == "__main__":
    main()
