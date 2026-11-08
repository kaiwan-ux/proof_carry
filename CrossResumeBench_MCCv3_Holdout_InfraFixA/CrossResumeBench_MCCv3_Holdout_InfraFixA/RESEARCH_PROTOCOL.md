# Research Protocol — MCC v3 Holdout InfraFixA

## Status

Infrastructure-only rerun of the sealed MCC v3 closed-world holdout.

## Non-negotiable scientific freeze

The mechanism, holdout, evidence transformations, baselines, semantic oracle, evaluator and frozen scientific runner must retain the hashes in the original freeze records. InfraFixA may only change native execution containment and diagnostics.

## Native gate

For each of 8 semantic families and each runtime (LangGraph, CrewAI, Microsoft Agent Framework):

1. create a real native pause/checkpoint;
2. restore from that checkpoint;
3. reach the expected final semantic store;
4. return control cleanly to the harness.

Each probe executes in its own disposable process. Results are flushed after each probe. Timeouts and lifecycle hangs are capability/infrastructure failures, not MCC v3 outcomes.

## Full holdout

Only after 24/24 native probes pass:

- run 96 self-resume controls;
- run 96 source captures;
- run the sealed 6,144 cross-runtime migration evaluations;
- evaluate the same preregistered MCC v3 expectations;
- compare against frozen MCC v2 and the same baselines.

## Interpretation

- `safe_completion`: continuation matches oracle final state.
- `safe_rejection`: mechanism refuses an unproven continuation as preregistered.
- `unsafe_violation`: mechanism continues and violates the oracle/safety invariants.
- `technical_failure`: runtime/harness could not execute the condition.
- `semantic_complete_lifecycle_hang`: semantic state became correct but the native runtime did not return; this fails the native control and is not counted as an MCC result.

## Anti-contamination rule

Do not change MCC v3 or the sealed holdout based on InfraFixA outcomes. Any mechanism change after this holdout requires a new mechanism version and a fresh validation set.
