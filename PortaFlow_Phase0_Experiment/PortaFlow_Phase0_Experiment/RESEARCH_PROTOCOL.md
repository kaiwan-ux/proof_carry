# Research Protocol

## P0. Goal

Test whether continuation-sensitive semantics are lost by simple cross-runtime state transfer.

## P1. Unit of analysis

One run = `(source_runtime, target_runtime, workflow, condition, scenario_variant)`.

## P2. Runtime set

Primary: LangGraph, CrewAI, Microsoft Agent Framework.

## P3. Conditions

### naive_state

Transfer only ordinary state fields and the declared current step. Excludes hidden semantic commitments.

### state_history

Adds completed step names and normalized historical events. Still excludes privileged ground-truth semantic obligations such as effect replay bans or pending-approval contracts unless they are explicitly present in ordinary history.

### restart

Target starts from the beginning. This is expected to preserve final logical output in some cases but can replay work/effects and therefore is not automatically safe.

### oracle_full

Transfers all semantic ground truth from the scenario. This is a harness/expressibility upper bound. It is **not PortaFlow** and must not be presented as a contribution.

## P4. Ground-truth invariants

Every workflow has explicit hard invariants. A run is safe only when all hard invariants pass.

Common invariants:

- no duplicated irreversible effect,
- no skipped required step,
- no replay of a forbidden completed step,
- correct branch preservation,
- correct loop progress,
- retry budget preserved,
- pending approval preserved,
- correct final termination.

## P5. Technical failure policy

Dependency errors, framework API drift, serialization failures, import errors, timeouts and runtime crashes are recorded separately as `technical_failure=1`. They are never silently converted into semantic failures or dropped.

## P6. Statistics

Primary Phase-0 statistics are descriptive because deterministic cases can be exact. Report counts, proportions, pairwise matrices and Wilson 95% intervals for aggregated safe continuation proportions where there are repeated variants.

The LLM extension uses repeated runs and should add bootstrap or Wilson intervals as appropriate.

## P7. Interpretation

A semantic failure supports the research premise only when:

1. the source prefix executed correctly,
2. the target runtime executed technically,
3. the invariant violation is attributable to omitted/mismatched continuation information,
4. the `oracle_full` upper bound can continue correctly for the same scenario, or the limitation is explicitly classified as target-unrepresentable.

## P8. Anti-bias rules

- freeze metrics before inspecting final results,
- preserve all run records,
- do not hand-select only dramatic examples,
- distinguish technical failures from semantic failures,
- do not claim simulated/smoke output as native framework evidence,
- do not describe `oracle_full` as the proposed method.
