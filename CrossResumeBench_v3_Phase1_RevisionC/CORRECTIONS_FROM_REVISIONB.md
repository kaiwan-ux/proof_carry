# Corrections from Revision B to Revision C

Revision C is intentionally **not** a new MCC mechanism. It is a single-adapter correction to complete the Phase-1 native gate.

## Frozen / unchanged

The following are unchanged from Revision B:

- frozen MCC v2 source and schema
- two hidden worlds: `committed` and `not_committed`
- evidence variants: `enough_evidence` and `ambiguous_external_commit`
- LangGraph adapter
- CrewAI adapter and process-based native checkpoint method
- oracle and explicit-minimal controls
- target safety ledger and effect-decision oracle
- 72-row cross-runtime matrix
- gate thresholds

## Only research-runtime change

Microsoft Agent Framework (MAF) is corrected in `src/crossresumebench_v3_revc/native/maf_runtime.py`.

Revision B used local handler methods whose `WorkflowContext[...]` annotations were introspected by the framework and rejected at runtime. Revision C instead uses the framework's explicit handler declaration mode:

```python
@handler(input=str, output=str)
```

for forwarding executors, and:

```python
@handler(input=str, workflow_output=str)
```

for the terminal executor. This deliberately disables fragile handler-signature type introspection.

MAF source capture stops only after `superstep_completed`, then obtains the persisted checkpoint with `FileCheckpointStorage.get_latest(...)`. Native self-resume rebuilds the same workflow wiring and resumes with `checkpoint_id` plus the same checkpoint storage.

## New MAF-only gate

Before any 72-row migration run, Revision C executes:

```text
python scripts/probe_maf_revisionC.py
```

It must prove all of the following:

1. MAF capability imports succeed.
2. committed native checkpoint self-resume completes safely.
3. committed source capture stops before ack with effect_count=1.
4. not_committed source capture stops before ack with effect_count=0.
5. MAF target with `committed` skips the effect and finishes safely.
6. MAF target with `not_committed` executes the effect exactly once and finishes safely.

If this probe fails, Revision C does **not** run the full 72-row grid. It exports `CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip` instead.

## Scientific rule

A Revision-C MAF probe failure is an adapter/framework-integration result, not evidence against MCC v2. MCC v2 must remain frozen regardless of the probe result.
