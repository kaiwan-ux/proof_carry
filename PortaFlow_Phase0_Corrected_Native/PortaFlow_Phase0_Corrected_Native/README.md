# PortaFlow Phase-0 Corrected Native Experiment

This package replaces the earlier pseudo cross-framework matrix with **actual native executions** in LangGraph, CrewAI, and Microsoft Agent Framework (MAF).

## What it tests

At a declared migration-safe boundary, a source runtime executes the prefix of one of three continuation-sensitive workflows:

1. **Retry** — one tool attempt has already failed.
2. **Approval** — a human approval request is pending.
3. **Side effect** — an external payment-like effect has already committed.

The source's state is exported under three information conditions and an equivalent continuation is then executed by a **different real target runtime**.

There are 6 directed runtime pairs × 3 workflows = **18 core native migration cases**. Each case is run under 3 state-transfer conditions = **54 native target executions**.

## Conditions

- `naive_state`: ordinary application variables only.
- `state_history`: application variables + observable execution history; committed-vs-observed tool effect remains intentionally ambiguous.
- `native_semantic`: diagnostic privileged upper bound using source semantic fields/native snapshot. **This is not PCC and must not be claimed as the proposed method.**

## Why this is corrected

The earlier 1,080-row matrix repeated an abstract continuation model under framework labels. This version actually imports and executes LangGraph, CrewAI, and MAF adapters on both source and target sides. It also removes misleading confidence intervals from deterministic repeated cases.

## No LLM/API key is required

Phase-0 deliberately uses deterministic transitions. `GPT-OSS-120B` is configured only for a later extension and stays disabled.

## Windows quick run

Double-click `run_corrected_phase0.bat` or run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_corrected_phase0.ps1
```

After completion, send the entire `results/` folder back for analysis.

## Primary outputs

- `results/native_cross_runtime_runs.csv`
- `results/normalized_native_runs.jsonl`
- `results/native_sources/*.json` (9 real source captures)
- `results/native_targets/*.json`
- `results/probes/*.json`
- `results/condition_summary.csv`
- `results/pair_condition_summary.csv`
- `results/workflow_condition_summary.csv`
- `results/failure_taxonomy.csv`
- `results/PROPOSAL_EVIDENCE_SUMMARY.md`
- `results/technical_failures.json`
- `results/graphs/*.png`
- manifest/checksums

## Scientific claim boundary

This experiment tests **cross-runtime continuation at declared safe boundaries**. It does not claim arbitrary instruction-level process migration. It measures whether selected transferred state is sufficient to preserve hard behavioral invariants when the remaining workflow is executed by another real framework.
