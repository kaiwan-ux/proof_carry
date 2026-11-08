# Paper Output Map

Use these generated files when writing the paper after the final environment/native run is accepted:

- Main sealed baseline table: `results/tables/table_1_baselines.csv`
- Expanded120 table: `results/tables/table_2_expanded_results.csv`
- Ablation table: `results/tables/table_3_ablation.csv`
- Security table: `results/tables/table_4_security.csv`
- Semantic runtime mapping table: `results/tables/table_5_runtime.csv`
- Native status table: `results/tables/table_5b_native_status.csv`
- Performance/payload table: `results/tables/table_6_performance.csv`
- Rejection-reason table: `results/tables/table_7_rejection_reasons.csv`

Figures:

- `fig_1_safety.pdf`
- `fig_2_completion.pdf`
- `fig_3_ablation.pdf`
- `fig_4_security.pdf`
- `fig_5_latency.pdf`
- `fig_6_payload.pdf`

Statistical comparisons for the final release run are under `results/processed/<LATEST_RUN>/paired_safety_statistics.csv` and `paired_completion_statistics.csv`.

Do not substitute the semantic timing figure for native end-to-end timing; the native extension is separately gated.
