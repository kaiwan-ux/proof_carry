# Native Runtime Validation Protocol

Native validation is separate from semantic-runtime evaluation.

A runtime is marked **validated** only if all required operations are actually executed using the pinned runtime package:
1. construct the workflow in that framework;
2. reach the intended mid-execution pause;
3. capture a native artifact/checkpoint;
4. self-resume the source checkpoint as a control;
5. extract portable evidence from that real artifact;
6. run ProofCarry admission;
7. lower a verified continuation into the target runtime;
8. resume and check the externally observable outcome.

Import success, a runtime label, or a synthetic state object is **not** native validation.

The package preserves the previously passed 32-case native controls/source captures under `legacy_evidence/sealed_holdout_32/`. The new Expanded120 native extension is intentionally reported as NOT_RUN until the pinned framework adapters are executed.

Recommended pinned versions should be frozen from the environment used for the final run. Record them in the per-run `environment.json`.
