# Research Protocol — PCC v0 Ablation

## Goal

Move from *problem existence* to *mechanism testing* by determining which semantic continuation components are necessary for safe cross-runtime execution.

## Independent variable

Transferred continuation representation:

- state only
- state + semantic history
- + control frontier
- + pending obligations
- + effect receipts
- full PCC v0 (+ continuation/dependency contract)

## Controlled factors

- deterministic workflow logic
- no LLM
- same workflow semantics across frameworks
- deterministic mock external effect ledger
- same source state for each condition within a source/workflow pair
- hard invariant evaluation rather than subjective text similarity

## Dependent variables

Primary:

- Safe Continuation Rate (SCR)

Hard correctness failures:

- completed-step replay
- required-step skip
- duplicate external effect
- pending approval loss
- retry-state loss
- branch-decision loss
- loop-progress loss
- parallel-dependency loss
- wrong termination

Secondary:

- serialized PCC size
- framework-pair breakdown
- workflow-condition breakdown
- technical failure count

## Native source evidence

Each framework executes the prefix of each workflow and emits a native artifact:

- LangGraph checkpoint/state snapshot
- CrewAI Flow/persistence state
- MAF workflow checkpoint state

These native files are evidence/provenance only and are not inserted into PCC.

## Cross-runtime evaluation

For each ordered source/target pair where source != target:

1. execute the source prefix in the source framework;
2. capture source logical state and native evidence;
3. compile the selected PCC ablation representation;
4. lower the framework-neutral PCC into the target logical continuation state;
5. execute the remaining computation under the target framework;
6. evaluate hard invariants against the complete source+target logical execution;
7. store the native target artifact, PCC payload and evaluation.

## Hypotheses

### H1

Full PCC v0 has higher SCR than state-only and state+history baselines.

### H2

Effect receipts specifically prevent duplicate committed side effects.

### H3

Control frontier, pending obligations and dependency contracts yield distinct improvements on the workflow classes that require them.

## Kill criteria

- If `full_pcc_v0` does not materially outperform `state_history`, PCC v0 is not justified in its present form.
- If a proposed component never changes a hard-invariant outcome in its targeted workflow class, it should not be mandatory in PCC.
- Do not interpret semantic outcomes while unresolved technical framework failures remain.

## Statistics

This is a deterministic designed-case ablation, not an IID stochastic sample. Report descriptive counts/rates and per-workflow outcomes. Do not attach classical confidence intervals to repeated deterministic framework labels.

## Follow-up only after this passes

A later experiment may introduce GPT-OSS-120B with repeated runs, controlled prompts/tools, and proper stochastic statistics.
