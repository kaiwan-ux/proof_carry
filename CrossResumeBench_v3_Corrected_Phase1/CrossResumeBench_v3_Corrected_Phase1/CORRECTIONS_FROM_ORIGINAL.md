# Corrections from the original v3 design

## 1. MAF / AutoGen confusion fixed
The original roadmap incorrectly described MAF using `autogen.ConversableAgent` / `GroupChat`. This package uses Microsoft Agent Framework's `agent_framework` workflow/checkpoint APIs.

## 2. Native self-resume separated
A framework-native checkpoint is not a cross-framework migration baseline. It is a prerequisite control proving that the selected pause point is a real, resumable runtime state.

## 3. Unsupported boundaries are findings, not fake failures
A pause point can be:
- `native_checkpointable`
- `externally_blocked_capturable`
- `unsupported_at_this_boundary`

A framework is not penalized for an unsupported boundary unless the experiment claimed that boundary was natively checkpointable.

## 4. Evidence applicability matrix
The original Cartesian product applied every evidence degradation to every case. v3 now uses an applicability matrix. Example: `ambiguous_external_commit` is not applied to a retry-only workflow with no external effect.

## 5. Kill criteria corrected
- MCC unsafe on **enough evidence** remains a hard mechanism failure.
- Native self-resume failure is a hard validity failure only for a boundary classified as supported.
- Pair consistency is reported as exact paired discordance, not an arbitrary 50% variance threshold.
- Official AAIF/CapLease superiority claims remain prohibited until official artifacts are integrated.

## 6. Phase 1 before scale
The original design jumped toward 28 × 5 × 6 × 8. This package first validates real checkpoint extraction, self-resume, frozen-MCC translation, target-native continuation, and ambiguous-effect rejection on one common cross-runtime case.
