---
name: experiment-diagnosis
description: Diagnose a running or finished experiment and decide the next move — continue, switch phase, stop, or pivot — from the metric trajectory, its noise floor, and the method's known ceiling. Use when asking "how's it going / should I keep going or change approach?" about a training run or experiment series.
---

# Experiment diagnosis

Turn "how's it going?" into a defensible verdict. Where the experiment-loop skill *makes*
progress (edit → run → keep/discard), this decides whether progress has stalled and what to
do next — from the trajectory and the method's ceiling, not the latest number or a gut feel.
Pairs with the experiment-loop skill; adapted from
[karpathy/autoresearch](https://github.com/karpathy/autoresearch)'s fixed-metric discipline.

## Verdicts

Emit exactly one, backed by the evidence below:

- **CONTINUE** — the metric is still gaining more than its noise floor per unit of budget.
- **SWITCH** — the metric has converged (gain ≤ floor) OR sits at the current method's known
  ceiling; a different phase or method captures what is left.
- **STOP** — converged and at ceiling with no better phase available; ship the best checkpoint.
- **PIVOT** — the metric is not moving and the setup is suspect (wrong metric, dead signal,
  data leak); fix the setup before spending more budget.

## Protocol

1. **Pin the decision metric.** Held-out only — never the training loss. Training loss can fall
   via memorization while the held-out metric plateaus; diagnosing on it is self-deception. State
   its name and direction exactly as logged.
2. **Pull the whole trajectory, not the latest value.** One number is a status, not a diagnosis.
3. **Estimate the noise floor from the data** (cheapest available wins):
   - *Replicate* — re-run one identical config; the absolute difference is the floor. Gold
     standard, inherited from experiment-loop.
   - *Regressions in a monotone climb* — in a metric that should only improve, the size of each
     DOWNWARD step is pure noise. Mean |negative Δ| ≈ floor. Free: uses logs you already have.
   - *Rolling spread* — std of the per-step Δ after the opening transient.
   Record it. A floor from one or two regressions is weak — flag it as such.
4. **Compute the marginal gain.** Recent gain per budget unit (mean Δ over the last few steps)
   against the early gain and against the floor. A large early-to-recent ratio is the convergence
   signal.
5. **Apply the rule.** recent gain > floor → CONTINUE. recent gain ≤ floor → converged; go to 6.
6. **Name the ceiling.** Is the metric saturating against a *known limitation of the current
   method*? (L1 mel regresses to the blurry conditional mean; a proxy that saturates by design.)
   If yes, harder convergence is low-value and the remaining quality lives in another phase →
   SWITCH, even if a sliver of gain remains. If the plateau has no method explanation and the
   absolute values are implausible, suspect the setup → PIVOT.
7. **Cross-check with an independent signal.** Never trust one metric. Confirm the verdict against
   a second — a different eval metric, an absolute-value sanity check, a resource trend. Call out
   any metric that is meaningless in the current phase so it is not misread as signal (e.g. SI-SDR
   before any waveform-adversarial training).
8. **Emit the verdict block** (below). For CONTINUE/SWITCH, give the exact next command and which
   checkpoint to carry forward — usually the peak held-out one, not the latest.

## Cheap-insurance rule

Near the floor with a weak floor estimate, an irreversible next step is not worth a coin flip.
Spend a small confirmation budget first (a couple more units), state the cost asymmetry out loud
("2 more epochs ≈ 74 min vs ~0 expected gain"), and let the confirmation decide. Reversible next
steps need no insurance.

## Confirmation rule

Reversible moves (spawn the next run, read a checkpoint): just do them. Irreversible ones (kill a
live job, delete data, overwrite the incumbent): recommend and confirm — never unilaterally.

## Verdict block

```
VERDICT: SWITCH  (eval/stoi converged at method ceiling)
metric      early Δ/unit   recent Δ/unit   noise floor   rule
eval/stoi   +0.021         -0.001         0.010         recent ≤ floor → converged
ceiling     L1 mel saturates at PESQ 1.49 (clean ≈ 4.5); remaining quality needs the GAN phase
cross-check 4/4 languages plateaued; SI-SDR ignored (meaningless pre-GAN)
carry       stage1_00009.pth (peak held-out 0.8157, not the latest 0.8068)
next        <exact command to run>
```

## Autonomy

Diagnose from the evidence, not the hope. A flat held-out metric under a still-falling training
loss is convergence, not "almost there". Report the verdict even when it is STOP or "you have been
spending budget for nothing" — that honesty is the whole value of the skill.
