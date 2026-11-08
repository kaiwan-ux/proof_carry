# Build Validation

This package was validated before delivery without substituting fake adapters for the real native run.

## Passed during packaging

- Python compilation: PASS
- Unit/design tests: **9/9 PASS**
- Frozen MCC v2 hashes: PASS
- Two-world ambiguous payload identity unit test: PASS
- Frozen MCC v2 ambiguity rejection unit test: PASS
- Certified committed/not-committed reconstruction unit test: PASS
- Exact synthetic orchestration: **3 self-resume + 6 source captures + 72 migration rows**
- Synthetic MCC result: **12 safe completions + 12 safe rejections + 0 unsafe + 0 technical failures**
- Synthetic six-pair summary consistency: PASS
- Native unsafe self-resume classification test: PASS (unsafe native restore is not mislabeled technical)
- AutoGen/MAF confusion scan: PASS
- `WorkflowContext[dict]` scan: PASS (none)
- CrewAI Flow-event suppression scan: PASS (not enabled)
- Full-v3 flag disabled: PASS

## Runtime validation not executed in packaging environment

The packaging container cannot install the three pinned framework packages because outbound package-network access is unavailable. Therefore the real LangGraph/CrewAI/MAF run is deliberately left to the user's environment.

`preflight.py` checks exact pinned versions before executing:

- LangGraph 1.2.11
- CrewAI 1.15.17
- agent-framework-core 1.15.0

The real runner never substitutes fake adapters.
