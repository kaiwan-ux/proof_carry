# Research Protocol — Corrected Phase-0

## Primary question

When a deterministic stateful agent workflow reaches a declared migration-safe boundary, is ordinary application state sufficient for another agent framework to continue the remaining computation without replaying completed work, bypassing pending approval, duplicating committed effects, or corrupting retry semantics?

## Independent variables

- Source framework: LangGraph / CrewAI / Microsoft Agent Framework
- Target framework: the other two frameworks (6 directed pairs)
- Workflow: retry / approval / committed side-effect
- Transfer condition: naive_state / state_history / native_semantic diagnostic upper bound

## Controlled variables

The business transitions, identifiers, workflow boundaries, simulated user approval, and mock external effect semantics are deterministic and held constant. No LLM is used.

## Hard invariants

- Completed source-prefix steps must not be replayed.
- Retry attempt #1 must not be repeated after migration.
- A pending approval must be consumed before protected execution.
- A committed external effect must not execute twice.
- Required continuation steps must not be skipped.
- The workflow must terminate in the expected state.

## Primary metric

Safe Continuation Rate (SCR) = safe native migrations / valid native migration runs.

Because the 18 cases are a deterministic designed case set rather than IID random samples, Phase-0 reports descriptive counts/rates and **does not attach Wilson confidence intervals**.

## Gate

A strong gap claim is killed/pivoted if `naive_state` preserves all hard invariants in at least 17/18 core directed native migration cases. Technical failures are not counted as semantic failures; they must be fixed and rerun.

## Evidence tiers

1. **Primary:** native cross-runtime executions (`native_cross_runtime_runs.csv`).
2. **Supporting:** framework-specific checkpoint/persistence probes.
3. **Diagnostic only:** `native_semantic` upper bound.

Do not use the old abstract 1,080-run framework-labeled matrix as primary evidence.
