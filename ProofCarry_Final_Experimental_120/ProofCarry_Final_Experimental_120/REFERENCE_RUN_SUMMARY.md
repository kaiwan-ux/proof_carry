# Reference Deterministic Run Summary

**Run ID:** `proofcarry-20260829T201030Z-93eb8fd9`  

This run validates the package implementation in the current environment. It is not a substitute for the final pinned native-runtime run.

## Expanded120 semantic benchmark

- 120 base cases: 8 families x 15 cases.
- 7 evidence conditions x 6 directed runtime pairs = **5,040 ProofCarry conditions**.
- ProofCarry: **1,440 safe completions**, **3,600 safe rejections**, **0 unsafe continuations**.
- Always Reject: **0 safe completions**, **5,040 safe rejections**, **0 unsafe**.

## Security

- `authenticated_proofcarry`: 720 safe completions, 6,480 safe rejections, 0 unsafe.
- `hash_only_control`: 720 safe completions, 1,440 safe rejections, 5,040 unsafe.

## Ablation

- `full`: 720 complete, 4,320 reject, 0 unsafe.
- `minus_authentication`: 720 complete, 3,600 reject, 720 unsafe.
- `minus_certificate_verification`: 720 complete, 3,600 reject, 720 unsafe.
- `minus_closed_world`: 720 complete, 3,600 reject, 720 unsafe.
- `minus_complete_snapshot`: 576 complete, 3,888 reject, 576 unsafe.
- `minus_dependency_reasoning`: 720 complete, 3,600 reject, 720 unsafe.
- `minus_identity_binding`: 720 complete, 3,600 reject, 720 unsafe.

## Runtime-specific semantic identity

- `ambiguous`: 0 complete, 720 reject, 0 unsafe.
- `correct`: 720 complete, 0 reject, 0 unsafe.
- `missing`: 0 complete, 720 reject, 0 unsafe.
- `wrong`: 0 complete, 720 reject, 0 unsafe.

## Performance (semantic end-to-end harness)

- `total_ms`: median 0.0682, p95 0.1217, p99 0.2570, mean 0.0872.
- `total_transferred_bytes`: median 2548.5000, p95 3339.0500, p99 3485.0000, mean 2735.2167.

These timings are semantic-pipeline measurements on this machine, not native framework end-to-end migration latency.

## Native status

The expanded 120-case native run is **NOT RUN** in this build environment because the native framework packages are not installed. Prior passed native evidence for the original 32-case holdout remains under `legacy_evidence/sealed_holdout_32/`.
