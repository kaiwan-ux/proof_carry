# Phase-0 Automated Analysis Summary

> IMPORTANT: the systematic matrix in `raw_runs.csv` is marked `controlled_model`. It tests capsule sufficiency and must not be described as native framework evidence. Native framework probes are reported separately.

Total controlled runs: **1080**
Technical failures: **0**

## Safe Continuation Rate by condition

| Condition | Runs | Safe | SCR | 95% Wilson CI |
|---|---:|---:|---:|---:|
| naive_state | 270 | 90 | 0.333 | [0.280, 0.392] |
| oracle_full | 270 | 270 | 1.000 | [0.986, 1.000] |
| restart | 270 | 0 | 0.000 | [0.000, 0.014] |
| state_history | 270 | 225 | 0.833 | [0.784, 0.873] |

## Failure taxonomy

- **COMPLETED_STEP_REPLAYED**: 450
- **DUPLICATE_EXTERNAL_EFFECT**: 135
- **HUMAN_APPROVAL_LOST**: 45

## Decision rule

Do not make the final GO/NO-GO decision from the controlled model alone. Use it to validate the measurement pipeline, then inspect `native_probe_summary.csv` and the native JSON artifacts. If native evidence plus controlled continuation tests show repeated losses around multiple semantic categories, proceed to PCC v0. If ordinary state is sufficient in native cross-runtime implementations, pivot.