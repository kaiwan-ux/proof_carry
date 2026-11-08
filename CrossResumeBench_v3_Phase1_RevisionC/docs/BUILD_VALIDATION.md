# Build Validation — Revision C

This package was validated structurally before delivery without substituting fake adapters for the real native run.

## Passed during packaging

- Python compilation: PASS
- Unit/design tests: **11/11 PASS**
- Frozen MCC v2 hashes: PASS
- Two-world ambiguous payload identity unit test: PASS
- Frozen MCC v2 ambiguity rejection unit test: PASS
- Certified committed/not-committed reconstruction unit test: PASS
- Exact synthetic orchestration: **3 self-resume + 6 source captures + 72 migration rows**
- Synthetic MCC result: **12 safe completions + 12 safe rejections + 0 unsafe + 0 technical failures**
- Synthetic six-pair summary consistency: PASS
- Native unsafe self-resume classification: PASS
- AutoGen/MAF confusion scan: PASS
- Revision-C MAF explicit-handler static validation: PASS
- No `WorkflowContext[...]` introspection dependency in MAF adapter: PASS
- MAF checkpoint boundary contains `superstep_completed`: PASS
- MAF uses `get_latest(workflow_name=...)` and checkpoint-id restore: PASS
- Full-v3 flag disabled: PASS

## Why the MAF-only pre-gate exists

The packaging environment does not have the pinned Microsoft Agent Framework runtime installed, so a real MAF checkpoint cannot be honestly claimed here. Revision C therefore requires `scripts/probe_maf_revisionC.py` to pass on the user's pinned environment before the 72-row grid is allowed to run.

Pinned versions checked by `preflight.py`:

- LangGraph 1.2.11
- CrewAI 1.15.17
- agent-framework-core 1.15.0

The real runner never substitutes fake adapters.
