# Build Validation

This package was validated before delivery without executing the three real external framework runtimes.

## Passed checks

- Python compilation: PASS
- Unit/design tests: **7/7 PASS**
- Frozen MCC v2 hashes: PASS for `mcc.py`, `certificates.py`, `models.py`, and `mcc_v2.schema.json`
- Two-world ambiguous payload identity test: PASS
- Frozen MCC v2 ambiguous admissibility test: PASS (`AMBIGUOUS_EXTERNAL_COMMIT`)
- Certified committed/not-committed reconstruction test: PASS
- Exact synthetic orchestration shape: **3 self-resume + 6 source captures + 72 migration rows**
- Synthetic MCC result: **12 safe completions + 12 safe rejections + 0 unsafe + 0 technical failures**
- Full-v3 flag disabled: PASS
- AutoGen/MAF confusion scan: PASS (no AutoGen import in v3 source)

## Not executed during packaging

The packaging environment does not contain the pinned LangGraph, CrewAI, and Microsoft Agent Framework runtime stack. Therefore the real native Phase-1 run must be performed on the user's environment after `pip install -r requirements.txt`.

This is intentional: the package does not substitute fake adapters when executing `run_phase1_revisionA.ps1`. Preflight fails if a required native runtime is unavailable.
