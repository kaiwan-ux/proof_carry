# Proposal-Ready Experiment Description

## Preliminary result already established

A preceding native Phase-0 experiment found that ordinary application-state transfer was insufficient in selected continuation-sensitive workflows, while execution history repaired retry/approval cases but remained insufficient for committed external side effects. This motivated a new mechanism rather than a larger adapter layer.

## Next experiment — PCC v0 ablation

We introduce a **Portable Continuation Capsule (PCC v0)** that represents framework-independent logical continuation semantics. PCC is tested cumulatively using application state, semantic history, control frontier, pending obligations, effect receipts and a continuation/dependency contract.

Equivalent deterministic workflow prefixes are executed natively in LangGraph, CrewAI and Microsoft Agent Framework. Each source state is translated into each PCC ablation form and lowered into each different target runtime. Hard correctness contracts measure replay, duplicate effects, approval/retry preservation, branch/loop progress, parallel dependencies and termination.

The experiment uses six workflow classes and six directed framework pairs. With six ablation conditions this gives 216 configured target executions plus 18 native source captures. No LLM is used at this stage, isolating continuation/runtime effects from model stochasticity.

## Primary research question

> What is the minimum framework-independent semantic information required to safely continue an in-progress agent workflow on another runtime?

## Main falsifiable hypothesis

Full PCC v0 should preserve more hard continuation invariants than ordinary state or state+history. Ablation determines whether each additional semantic category is actually necessary; components that provide no measurable benefit are removed or demoted.
