
# Research Protocol — CrewAI Repaired Gate

## Frozen elements
- MCC v2 source/schema/certificate logic are copied byte-for-byte from Phase-1 Revision C and SHA-256 verified.
- Two-world semantics are unchanged.
- Evidence variants are unchanged.
- Safety oracle is unchanged: final ledger must be `{effect_count:1, ack_count:1, finish_count:1}`.
- Frozen MCC v2 must never be edited based on this gate result.

## CrewAI-only scope
This package intentionally includes **only CrewAI**. It is not a cross-framework generalization experiment and must not be described as one.

## Native repair probe
Before the 12-row matrix, the experiment checks:
1. CrewAI checkpoint capabilities are available.
2. committed native self-resume is technically executable.
3. committed source capture stops before ACK.
4. not-committed source capture stops before ACK.
5. target decision `committed` skips the effect and finishes safely.
6. target decision `not_committed` executes exactly once and finishes safely.

If any probe check fails, the full grid is not run.

## Focused scientific gate
After probe PASS:
- source = CrewAI
- target = CrewAI
- worlds = committed, not_committed
- evidence = enough_evidence, ambiguous_external_commit
- methods = mcc_v2, oracle, explicit_minimal
- total migration rows = 12

## Gate interpretation
PASS supports the narrow claim that the repaired CrewAI adapter is usable for this native pause/continuation pattern and that frozen MCC v2 behaves correctly on the focused two-world CrewAI gate.

PASS does **not** establish universal CrewAI workflow migration, all CrewAI versions, or general cross-runtime safety.
