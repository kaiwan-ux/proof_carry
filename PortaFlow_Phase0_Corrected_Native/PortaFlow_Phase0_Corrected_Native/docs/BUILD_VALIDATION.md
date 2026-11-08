# Build Validation

Validation performed before delivery:

- Python source compilation: **PASS**.
- Deterministic semantic unit tests: **4/4 PASS**.
- Full 54-row orchestrator/output pipeline with fake framework adapters: **PASS**.
- Matrix verifier: **PASS** on the validation pipeline (54 unique rows, all expected cases present).
- Analysis/report/graph generation pipeline: **PASS** on validation data.
- Validation outputs were deleted before packaging so the delivered `results/` directory starts clean.

The ChatGPT container used to build this package does not have the three native frameworks installed and has no package-download network access, so the real native framework run was not fabricated here. The package pins the same runtime family seen in the user's previous Windows run (`langgraph 1.2.11`, `crewai 1.15.17`, `agent-framework-core 1.15.0`). The corrected Microsoft Agent Framework probe follows the current official checkpoint pattern: concrete `WorkflowContext[...]` annotations plus `on_checkpoint_save` / `on_checkpoint_restore`, and intentionally does not use postponed string annotations.

A real run is considered valid only when `scripts/verify_results.py` reports PASS and `technical_failures.json` contains no native source/target failures.
