# Final Experiment Matrix

| Experiment | Question | Unit / Scale | Main Outputs |
|---|---|---|---|
| Sealed controlled holdout | Is the mechanism safer than baselines on the original frozen evidence? | Preserved 32-case / 6,144-row holdout | `legacy_evidence/sealed_holdout_32/`, `table_1_baselines.csv` |
| Expanded120 semantic | Does behavior persist across broader semantic scenarios? | 120 cases, 7 evidence conditions, 6 directed pairs, 8 methods | `expanded120.csv`, `table_2_expanded_results.csv` |
| Ablation | Which mechanisms produce selective safety? | 120 cases x 6 pairs x 7 challenges x 7 configurations | `ablation.csv`, `table_3_ablation.csv` |
| Authenticated security | Can evidence manipulation bypass admission? | 120 cases x 6 pairs x 10 conditions x 2 security modes | `security.csv`, `table_4_security.csv` |
| Runtime-specific semantics | Can semantic identities be established across heterogeneous runtime representations? | 120 cases x 6 pairs x 4 mapping conditions | `runtime_identity.csv`, `table_5_runtime.csv` |
| Native runtime validation | Does a real runtime capture/self-resume/lower/resume? | Explicitly gated by installed/pinned framework adapters | `results/native/`; prior evidence under `legacy_evidence/` |
| End-to-end performance | What does semantic proof-carrying migration cost? | 120 cases x 6 pairs x 30 measured repetitions after warmup | `performance.csv`, `table_6_performance.csv` |

The native experiment is deliberately not conflated with the semantic runtime experiment.
