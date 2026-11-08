# CrossResumeBench v1 — Publication Benchmark

This repository is the next-stage benchmark for **Minimal Certified Cross-Runtime Continuation (MCC)**. It is designed to answer a narrower, publication-relevant question:

> When a running agent workflow is translated between heterogeneous runtimes, which semantic facts can be reconstructed safely, which require certified evidence, and when must migration be rejected?

## Important design rule
MCC is frozen *before* the generated benchmark suite is frozen. `benchmark/FROZEN_MCC_SHA256.txt` fingerprints the mechanism. `benchmark/FROZEN_SUITE_SHA256.txt` fingerprints the suite and `FROZEN_BENCHMARK_CODE_SHA256.txt` fingerprints the generator/evaluator semantics. The run script verifies these hashes; it does not silently refreeze them. Do not edit MCC or benchmark semantics after seeing results—make a new version instead.

## Two evidence layers
1. **Semantic stress suite:** 60 new generated cases × 11 conditions = **660 runs**. These cases combine approval, retries, loops, parallel joins, callbacks, compensation, one-to-many/many-to-one semantic mappings, and ambiguous external effects.
2. **Native confirmation:** 12 frozen canonical cases × 6 directed framework pairs × 7 selected conditions = **504 target executions** across LangGraph, CrewAI, and Microsoft Agent Framework.

The native stage executes the normalized continuation *inside* each target runtime. It does **not** directly import a LangGraph binary/native checkpoint into CrewAI or MAF; do not claim direct native-checkpoint interchange.

## Baselines
`state_only`, `raw_history`, `history_inference`, `native_restart`, `aaif_state_strict`, `caplease_inspired`, `aaif_plus_caplease`, `explicit_minimal`, `full_pcc`, `mcc`, `oracle`.

`aaif_*` and `caplease_inspired` are **reference abstractions only**. They are intentionally labelled so the paper cannot falsely claim an official implementation comparison. Replace them with the authors' official artifacts before making a direct superiority claim.

## Run
Windows PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_crossresumebench.ps1
```
Or double-click `run_crossresumebench.bat`.

No LLM/API key is required.

At completion upload `CrossResumeBench_v1_results.zip` for analysis.
