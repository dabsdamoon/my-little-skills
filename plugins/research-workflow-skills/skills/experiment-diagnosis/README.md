# experiment-diagnosis skill

Portable, agent-agnostic decision protocol for the question "how's it going — keep going or
change approach?". `SKILL.md` is the canonical source; it is plain markdown with no code
dependency, so any coding agent can follow it.

Where the `experiment-loop` skill runs the keep/discard iteration, this one reads the state that
loop (or any training run) has produced and returns a verdict — CONTINUE / SWITCH / STOP / PIVOT —
with the evidence: metric trajectory, a noise floor estimated from the data, the marginal-gain
rule, the method's known ceiling, and an independent cross-check.

## Install

**Claude Code, all projects (personal skill):**

```bash
mkdir -p ~/.claude/skills/experiment-diagnosis
cp SKILL.md ~/.claude/skills/experiment-diagnosis/SKILL.md
```

Invoke with `/experiment-diagnosis` or let the model pick it up from the description.

**Claude Code, one project:** copy the directory to `<repo>/.claude/skills/experiment-diagnosis/`.

**Codex CLI:**

```bash
mkdir -p ~/.codex/prompts
cp SKILL.md ~/.codex/prompts/experiment-diagnosis.md
```

**Any other agent:** point it at `SKILL.md` in your first message.

## Provenance

Generalizes the noise-floor discipline of the `experiment-loop` skill (adapted from
[karpathy/autoresearch](https://github.com/karpathy/autoresearch)) from a per-run keep/discard
decision to a stop/switch/pivot decision over a whole trajectory. Key additions:

- **Noise floor from the curve itself** — the downward steps of a should-be-monotone metric
  approximate the floor for free, when replicating an identical run is too expensive.
- **Name the ceiling** — a metric saturating against a known limitation of the method (L1
  oversmoothing, a proxy that saturates by design) is a switch-phase signal, not a train-longer
  signal.
- **Decide on the held-out metric, never the training loss** — a falling train loss under a flat
  eval metric is convergence, not progress.
- **Cheap-insurance and confirmation rules** — a weak floor estimate near convergence buys a small
  confirmation budget before any irreversible switch.
