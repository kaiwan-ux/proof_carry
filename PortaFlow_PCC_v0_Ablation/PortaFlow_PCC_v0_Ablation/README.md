# PortaFlow — PCC v0 Native Ablation Experiment

This is the **next experiment after Phase-0 problem discovery**. Phase-0 showed that ordinary state transfer can be insufficient for continuation and that committed external effects are especially problematic. This package now tests the proposed mechanism: a **Portable Continuation Capsule (PCC v0)**.

## Research question

> What is the minimum framework-independent semantic information required to safely continue an in-progress agent workflow on another agent runtime?

## Primary frameworks

- LangGraph
- CrewAI Flows
- Microsoft Agent Framework (MAF)

The package pins the versions that were successfully used in the preceding native experiment:

- `langgraph==1.2.11`
- `crewai==1.15.17`
- `agent-framework-core==1.15.0`

## Six workflow classes

1. `retry` — migration after a failed first tool attempt.
2. `approval` — migration while a human approval is pending.
3. `side_effect` — migration after an external payment-like effect committed.
4. `branch` — migration after a branch decision but before branch execution.
5. `loop` — migration after two of three loop iterations.
6. `parallel` — migration after one fan-out branch completed but before the join.

## Six cumulative ablation conditions

1. `state_only`
2. `state_history`
3. `plus_control_frontier`
4. `plus_pending_obligations`
5. `plus_effect_receipts`
6. `full_pcc_v0`

The conditions are cumulative. Each stage adds one semantic category so we can measure marginal benefit.

## Native migration matrix

Three frameworks produce six directed cross-runtime pairs. With six workflows and six conditions:

`6 framework directions × 6 workflows × 6 conditions = 216 target executions`

There are also `3 frameworks × 6 workflows = 18` native source captures.

## Critical anti-cheating rule

`full_pcc_v0` does **not** contain a source-native LangGraph/CrewAI/MAF checkpoint blob. Only framework-neutral semantic data is carried. Native snapshots are kept as research evidence/provenance files outside the PCC.

## No LLM in this experiment

No API key is needed. GPT-OSS-120B is intentionally excluded so framework/continuation effects remain deterministic. `.env.example` is only reserved for the later stochastic experiment.

## Run on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_pcc_v0.ps1
```

or double-click `run_pcc_v0.bat`.

## Main output

After a successful run, upload:

`PortaFlow_PCC_v0_results.zip`

The result package includes raw rows, every PCC payload, framework-native source/target evidence, graphs, component gains, failure taxonomy, environment, checksums, and a proposal-ready evidence summary.

## Scientific claim boundary

This experiment studies **structured workflow continuation at declared safe migration boundaries**. It does not claim arbitrary instruction-pointer/process migration, universal support for every framework primitive, or perfect equivalence for arbitrary LLM agents.

See `docs/CLAIM_BOUNDARIES.md` before writing proposal claims.
