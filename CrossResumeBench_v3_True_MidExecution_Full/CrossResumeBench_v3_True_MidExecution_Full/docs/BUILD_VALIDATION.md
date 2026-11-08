# Build Validation

Before packaging, the benchmark is required to pass:
- Python compilation
- frozen MCC v2 hash verification
- suite/applicability/evaluation-code freeze verification
- structural pytest suite
- a synthetic 3,360-row orchestration using fake runtimes (orchestration only; not scientific evidence)
- exact row accounting

The synthetic run is intentionally allowed to reveal unsafe degraded-evidence MCC behavior; it is not used to tune or modify frozen MCC v2. Only enough-evidence correctness and infrastructure integrity are required pre-run.
