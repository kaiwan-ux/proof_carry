# Build Validation

Before delivery, the package was validated without installing the external agent frameworks in the build container.

Validation performed:

- Python source compilation: PASS
- PCC/evaluator unit tests: 5/5 PASS
- anti-native-checkpoint-leak test: PASS
- cumulative semantic-section test: PASS
- full 216-row matrix generation using deterministic fake framework adapters: PASS
- unique run IDs: PASS
- analysis pipeline: PASS
- graph generation pipeline: PASS
- result completeness verifier: PASS
- manifest/checksum pipeline: PASS

The fake-adapter validation exists only to verify experiment machinery. Its outputs are removed before delivery and are **not research evidence**. Actual evidence is created only when the user runs the package with LangGraph, CrewAI and Microsoft Agent Framework installed.
