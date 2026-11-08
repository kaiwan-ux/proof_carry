# PortaFlow Phase-0 Experiment

## Purpose

This package is the **problem-existence experiment** for the PortaFlow FYP/research direction.
It is deliberately built **before** the proposed Portable Continuation Capsule (PCC).

The research question for Phase-0 is:

> When an in-progress logical agent workflow is moved between heterogeneous agent runtimes, is ordinary application state sufficient to continue correctly, or are additional execution semantics required?

The package tests six continuation-sensitive workflow patterns across:

- LangGraph
- CrewAI Flows
- Microsoft Agent Framework (MAF)

It uses deterministic logic by default so framework/runtime behavior is not confounded by LLM randomness.
An optional Groq GPT-OSS-120B path is included for a later stochastic extension.

## Important scientific boundary

This folder contains **no claimed PortaFlow solution**. The `oracle_full` condition is an experimental upper bound only. It exists to show whether the harness can continue a workflow when all ground-truth semantic facts are supplied. It must not be reported as the proposed method.

## Experiments

### E0 — Native runtime semantics probes

Framework-specific scripts inspect/check same-runtime persistence and resume behavior.
These probes are evidence that the runtimes expose different checkpoint/resume surfaces.

### E1 — Controlled cross-runtime continuation baselines

Equivalent deterministic workflows are executed to a migration boundary. A baseline capsule is exported and the target runtime reconstructs the remaining logical execution.

Conditions:

1. `naive_state` — user/application variables + current step only.
2. `state_history` — adds completed-step/history information.
3. `oracle_full` — all semantic ground truth; **upper-bound sanity check, not the proposed method**.
4. `restart` — target restarts from the beginning.

### E2 — Optional LLM extension

Disabled by default. Uses Groq's OpenAI-compatible endpoint with model `openai/gpt-oss-120b` when `GROQ_API_KEY` is present.

## Six workflows

1. `linear` — pause after B in A→B→C→D.
2. `branch` — branch already chosen before migration.
3. `loop` — migration after loop iteration 2 of 3.
4. `retry` — migration after first failed attempt.
5. `approval` — migration while waiting for approval.
6. `side_effect` — migration immediately after an irreversible mock payment.

## Main correctness metrics

- Safe Continuation Rate (SCR)
- Duplicate External Effect Rate
- Required-Step Skip Rate
- Completed-Step Replay Rate
- Approval Preservation Rate
- Retry Preservation Rate
- Correct Termination Rate
- Technical Failure Rate

A run counts as **safe** only if every hard invariant for that workflow passes.

## Fastest proposal-ready path

On Windows:

```powershell
run_phase0.ps1
```

or:

```bat
run_phase0.bat
```

The script:

1. creates `.venv`,
2. installs dependencies,
3. performs preflight checks,
4. runs core unit tests,
5. runs the controlled Phase-0 matrix,
6. attempts native framework probes,
7. analyzes results,
8. generates graphs/reports/checksums.

If a native framework API changed, that probe is logged as a **technical failure** rather than silently discarded.

## Where results are saved

Everything is placed in `results/`:

```text
results/
├── raw_runs.csv
├── normalized_traces.jsonl
├── execution_summary.csv
├── failure_cases.csv
├── framework_pair_summary.csv
├── workflow_summary.csv
├── failure_taxonomy.csv
├── native_probe_summary.csv
├── graphs/
│   ├── safe_continuation_rate.png
│   ├── failures_by_workflow.png
│   ├── failure_type_distribution.png
│   ├── framework_pair_matrix.png
│   └── invariant_pass_rates.png
├── ANALYSIS_SUMMARY.md
├── EXECUTION_REPORT.txt
├── ENVIRONMENT.json
├── CONFIG_SNAPSHOT.json
├── MANIFEST.json
└── CHECKSUMS_SHA256.txt
```

Send the full `results/` folder back for independent analysis.

## API key

**Phase-0 deterministic mode requires no API key.**

For the optional LLM extension:

1. copy `.env.example` to `.env`,
2. set `GROQ_API_KEY=...`,
3. keep `LLM_MODEL=openai/gpt-oss-120b`,
4. run `python scripts/run_llm_extension.py`.

Do not commit `.env`.

## Proposal go/no-go rule

The hypothesis survives if ordinary state/history transfer produces meaningful invariant violations across representative patterns while the full-information upper bound demonstrates that those failures are attributable to missing continuation semantics rather than an impossible target implementation.

The idea should be reconsidered if naïve state transfer achieves approximately >=95% safe continuation on the representative suite and extra semantic information provides negligible benefit.

## Reproducibility

- fixed scenario inputs,
- deterministic tools,
- stable run IDs,
- normalized event schema,
- raw data retained,
- environment captured,
- configuration snapshot retained,
- SHA256 checksums generated,
- technical failures preserved rather than removed.

## Python

Recommended: Python 3.11 or 3.12.
