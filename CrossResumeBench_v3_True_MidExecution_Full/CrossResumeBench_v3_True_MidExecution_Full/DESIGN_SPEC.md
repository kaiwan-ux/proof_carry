# Full v3 Design Specification

## Core invariant
Source frameworks are actually executed to a durable mid-execution checkpoint. The transfer package is restricted to MCC v2's schema (`app_state + history + certificates` plus provenance fields). Target frameworks execute a fresh target-native continuation workflow derived only from the lowered transfer representation.

## Stages
1. environment + frozen-hash verification
2. local structural tests
3. 21 native family probes (3 frameworks × 7 families)
4. 84 native self-resume controls + 84 native source captures
5. 3,360 cross-runtime migration evaluations
6. analysis, exact-row verification, manifest, export

## Evidence applicability
- effect: enough, ambiguous external commit
- retry: enough, partially observable progress, conflicting granularity
- approval: enough, partially observable progress
- parallel: enough, missing semantic completion, partially observable progress, conflicting granularity
- loop: enough, partially observable progress, conflicting granularity
- compensation: enough, ambiguous external commit, partially observable progress
- callback: enough, partially observable progress, conflicting granularity

Degraded variants are deliberately allowed to expose MCC limitations. They are not engineered to guarantee rejection.

## Primary metrics
- Safe Completion Coverage (SCC)
- Safe Rejection Rate
- Unsafe Continuation Rate (primary safety metric)
- technical failure rate
- family/pair consistency
- payload bytes
- replay/duplicate/missing-state mismatch taxonomy via semantic-store equality

## Gates
Infrastructure gate requires exact rows and zero native/MCC technical failures. Scientific MCC gate requires all enough-evidence cases safe, and zero MCC unsafe across all evidence variants. If the scientific gate fails, characterize the failure; do not tune frozen MCC on this suite.
