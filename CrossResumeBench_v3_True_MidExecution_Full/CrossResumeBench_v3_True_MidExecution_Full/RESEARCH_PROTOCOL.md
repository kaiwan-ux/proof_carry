# Research Protocol

## Hypotheses
H1: Frozen MCC v2 safely completes every enough-evidence full-v3 case across all six directed runtime pairs.
H2: Frozen MCC v2 has zero unsafe continuations across the full evidence-degradation matrix; when continuation-critical facts cannot be proven it should reject rather than guess.
H3: MCC v2 separates from concept-level history/AAIF/CapLease references on safety-resolution trade-offs.

## Controls
`oracle` and `explicit_minimal` use evaluator-only truth and are privileged upper bounds, not deployable competitors. `aaif_reference`, `caplease_reference`, and `aaif_plus_caplease_reference` are independent concept-level reference implementations, not official author artifacts.

## Freeze discipline
MCC v2 is immutable. The case suite and applicability matrix are hashed before execution. Any post-result mechanism redesign becomes MCC v3 and must be evaluated on a fresh unseen holdout.

## Statistics
Use case-level paired outcomes, family-stratified counts, pair-level discordance and exact paired comparisons. Do not treat thousands of rows as independent samples without accounting for repeated measurements over the same base cases.
