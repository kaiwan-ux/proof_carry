# Build provenance

1. MCC v3 mechanism was implemented and frozen first: `4e6fdd6d0fc949a7e337b02be9d71706a40f5fc87971f8030e0a5a02a32f6194`.
2. A fresh random holdout seed was generated only after that freeze: `eaf7aa910c36f0e20aab4e6046edd5fe`.
3. The 32-case sealed holdout was generated: `3cc06e8817f1b1861381ec348bbcf769be4b169833b9b24deccfc688a154f8e8`.
4. Evidence lowering, evaluator, runner and baseline code were then frozen in `benchmark/EXPERIMENT_FREEZE_RECORD.json`.

This procedural separation is intended to prevent tuning MCC v3 against the prior full-v3 discovery cases or post-hoc editing after holdout inspection.
