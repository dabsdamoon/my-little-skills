# Choosing general LLM evaluation metrics

Reviewed 2026-11-18. Benchmark names denote specific datasets and protocols, not
generic labels for a few similar questions. Pin dataset revision, grader revision,
prompt, tools, few-shot examples, decoding/reasoning settings and sample count.

| Capability | Established evaluation / metric | Interpretation and limits |
|---|---|---|
| Broad knowledge and reasoning | [MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro), accuracy | Diverse subjects; fixed multiple-choice protocol. Sensitive to prompt and training contamination. |
| Difficult scientific reasoning | [GPQA](https://arxiv.org/abs/2311.12022), accuracy; identify exact split | Specialist science; not a general product-usefulness score. Do not compare different splits as identical. |
| Instruction following | [IFEval](https://arxiv.org/abs/2311.07911), prompt/instruction strict and loose accuracy | Programmatically verifiable constraints. Report which scoring variant was used. |
| Code generation | [HumanEval / EvalPlus](https://github.com/evalplus/evalplus), pass@1 with executable tests | Correctness against tests, not style. Distinguish pass@1 from best-of-k; execute generated code in a proper isolated sandbox. |
| Factuality and abstention | [SimpleQA](https://openai.com/index/introducing-simpleqa/), correct / incorrect / not attempted | Closed-book facts differ from retrieving an answer from supplied evidence. The official grader/protocol matters. |
| Grounded reading | Evidence-supported accuracy, contradiction and abstention rates on a frozen task-specific set | Cite source spans; separate unsupported claims from correctly refusing an unanswerable question. Original cases are not SimpleQA scores. |
| Korean / target language | Language-specific held-out tasks with exact or human-validated answers | English aggregate accuracy does not establish Korean quality. Specify language, domains and ambiguity policy. |
| Long context, vision and agents | Separate modality/tool/environment tasks and success rates | A short text pilot provides no estimate here. Tools and harness versions are experimental variables. |
| Reliability | Per-trial scores, dispersion, answer agreement, failures and completion coverage | Two repetitions of 24 questions are still 24 unique questions. Agreement can be consistently wrong. |
| Efficiency | End-to-end time, TTFT, generation tokens/s, input/cached/output/reasoning tokens, cost | Measure each separately. CLI wall time includes startup/network/queue; it is not TTFT. Subscription quota is not API dollar spend. |
| Calibration / robustness | Brier score or ECE with elicited probabilities; perturbation accuracy | Requires an explicit protocol and enough samples. Do not infer calibration from accuracy or attach fake precision to a tiny pilot. |

[HELM](https://crfm.stanford.edu/2022/11/17/helm.html) motivates multi-dimensional
evaluation rather than a single leaderboard scalar. OpenAI's
[evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
also stresses task-specific evals, logging and variability. This skill runs locally;
it does not depend on the hosted Evals platform.

## The bundled pilot

`assets/text-pilot.json` contains **24 original cases**, four each for reasoning,
stable knowledge, Python code comprehension, instruction following, supplied-source
grounding and Korean. Each answer is graded with type-sensitive exact equality.
Object key order is irrelevant; array order and string case matter. Missing IDs
fail their cases; extra IDs, duplicate JSON keys or invalid JSON fail the response.
There is no semantic judge, normalization or answer repair after collection.

Case accuracy = passed cases / all cases. Category macro = unweighted mean of
category accuracies; these coincide when categories have equal size. The strict
output protocol adds instruction-following demands to every category. This is a
**batched evaluation**: answers may interact within one context. It trades diagnostic
coverage and call count against per-question independence. It measures code reading,
not executable code generation, and basic knowledge questions may saturate.

Default: two fresh trials/model, sequential order ABBA for two models. Report both
trial scores, unique case count, category scores and answer stability. Never label
this pilot MMLU, GPQA, IFEval or HumanEval; never extrapolate a universal winner.
If both models saturate, report a ceiling. Pre-register any harder follow-up as a
new experiment; retain the original results and count the additional quota usage.

Transport/auth/model-unavailable failures have **N/A quality** and reduce coverage.
A completed response with invalid format receives zero. Any observed tool use is
a control violation, excluded from quality and prominently reported. Do not silently
turn infrastructure errors into wrong answers or drop failed cases from denominators.

Use official release scores as **manufacturer-reported evidence**, separate from
our measurement, with matching model family and inference settings. Model ID strings
may be moving aliases even when their names include versions. Record requested IDs;
only claim resolved snapshots when the runner independently exposes them.
