# Build Validation Report

This report records package-construction checks performed **before any paper result is claimed**.

## Passed in the build environment

- Suite shape: **104 unique base cases**, 8 families, 13 cases per family.
- `pytest`: **7/7 passed**.
- Python compilation: all `src/`, `mechanism/`, `scripts/`, and `tests/` modules compile.
- Freeze verification: suite SHA-256 matches `benchmark/SUITE_SHA256.txt`.
- Full sufficient-evidence synthetic check: all 104 cases produced a safe ProofCarry continuation.
- Full ProofCarry/Always-Reject evidence-condition validation: **6,240 rows**, 0 technical failures; ProofCarry had 0 unsafe outcomes, completed all sufficient/bound/noise conditions, and rejected all missing-fact/missing-binding conditions; Always Reject had zero completion coverage.
- Security harness validation: **11,232 rows**, 0 technical failures. ProofCarry accepted all 624 valid controls (104 cases x 6 directed runtime pairs) and rejected every configured attack. The unkeyed-hash control intentionally accepted replay/recomputed-hash/runtime-substitution/expiry/nonce-reuse/unauthorized-binding attacks, showing that the security test can detect the intended weakness.
- Ablation harness validation: **17,472 rows**, 0 technical failures. Full ProofCarry remained 0-unsafe in the synthetic validation; removing the closed-world gate produced unsafe outcomes, while removing identity binding or snapshots reduced completion coverage.
- All-method sufficient-evidence smoke matrix: **6,240 rows**, 0 technical failures across the 10 configured methods.

## Not rerun in this build container

The real LangGraph/CrewAI/Microsoft Agent Framework native stage was **not** executed here because those framework packages are not installed in this container. The package therefore does not ship fabricated native results. It reuses the previously validated runtime adapters and pins the same versions (`langgraph==1.2.11`, `crewai==1.15.17`, `agent-framework-core==1.15.0`). `scripts/preflight.py` is strict by default and `scripts/run_native.py` exits non-zero if the 24-probe family gate fails.

## Scientific rule

The validation above is a build/sanity check only. The deliverable `results/` directory is intentionally empty. Paper numbers must come from a fresh run of this frozen package on the intended experiment machine.
