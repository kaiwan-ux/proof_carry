# CrossResumeBench — MCC v3 Closed-World Holdout — InfraFixA

This package is an **infrastructure-only correction** of the frozen MCC v3 holdout experiment.

## Why InfraFixA exists

The first real holdout attempt stopped during the native-family gate. The recovered `work/` snapshot showed:

- LangGraph native probes: 8/8 completed correctly.
- CrewAI native probes: 3/8 completed correctly.
- MAF probes: not reached.
- The 6,144 migration grid never started.

The partial CrewAI compensation store had already reached the correct final semantic state, but the benchmark did not advance. That is consistent with a runtime/lifecycle hang in the harness rather than an MCC v3 result.

## Scientific freeze is unchanged

InfraFixA does **not** modify:

- `mechanism/mcc_v3.py`
- `mechanism/proofs.py`
- `mechanism/schemas/mcc_v3.schema.json`
- the 32-case holdout suite
- evidence generation
- baselines
- evaluator
- semantic oracle
- the frozen scientific runner
- frozen MCC v2 baseline

The original preregistered hashes are retained in `benchmark/EXPERIMENT_FREEZE_RECORD.json` and verified before every run.

## What InfraFixA changes

Only native-runtime orchestration changes:

1. Every native gate probe runs in an isolated Python subprocess.
2. Every native self-resume and source-capture call used by the frozen runner is isolated.
3. Each isolated call has a hard timeout and process-tree kill.
4. Native gate results are written **after every probe**, not only at the end.
5. A semantically completed but non-returning runtime is explicitly recorded as `semantic_complete_lifecycle_hang`; it is **not silently passed**.
6. Windows runs force UTF-8 and disable CrewAI tracing/telemetry noise.
7. One failed/hung native probe cannot block later CrewAI or MAF probes.
8. Scientific failures still export complete results when the row structure is valid.

## Experiment sizes

- Native family gate: 24 probes (8 families × 3 frameworks)
- Native self-resume controls: 96
- Source captures: 96
- Migration evaluations: 6,144

The migration matrix is unchanged from the sealed holdout.

## Native gate policy

The 6,144-row holdout starts only if all 24 native probes satisfy:

- restore completed
- semantic result safe
- runtime lifecycle returned cleanly
- no timeout
- no technical failure

If the semantic state reaches the oracle but the framework call never returns, the probe is diagnosed and the native gate fails. This prevents a lifecycle defect from being mislabeled as a valid checkpoint/resume control.

## Run on Windows

Use `run_mccv3_holdout_infrafixA.ps1`.

If the native gate fails, upload:

`CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip`

If the full run completes, upload:

`CrossResumeBench_MCCv3_Holdout_InfraFixA_results.zip`

Upload the result even when the scientific verdict is negative. Do not alter MCC v3 or the holdout after seeing the result.
