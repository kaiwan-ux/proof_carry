# Corrected Implementation Roadmap

## Gate 0 — freeze verification
Verify that the copied MCC v2 files match the archived v2 source hashes. Never change them in v3.

## Gate 1 — runtime capability probe
Confirm versions and API surfaces for LangGraph, CrewAI, and Microsoft Agent Framework. Produce `results/capabilities.json`.

## Gate 2 — native self-resume
Run the `effect_committed_ack_pending` checkpoint in each framework and verify same-framework resume produces exactly one effect and one acknowledgment.

## Gate 3 — cross-framework Phase 1
Run all six directions with:
- MCC v2 / enough evidence;
- MCC v2 / ambiguous external commit;
- oracle / enough evidence;
- explicit-minimal / enough evidence.

## Gate 4 — review
Proceed to full v3 only if:
- all supported native self-resume controls pass;
- all MCC enough-evidence migrations are safe;
- all MCC ambiguous-commit variants reject before target execution;
- no MCC payload violates v2 schema;
- all source artifacts prove unresolved target work exists;
- target execution uses native runtime control flow.

## Full v3 after gate
1. Add retry and approval cases only after capability proof.
2. Add parallel, loop, compensation, and callback cases one family at a time.
3. Apply only meaningful evidence variants.
4. Freeze the full suite before evaluating it.
5. Compare paired outcomes; do not inflate N by treating framework directions as independent cases.
