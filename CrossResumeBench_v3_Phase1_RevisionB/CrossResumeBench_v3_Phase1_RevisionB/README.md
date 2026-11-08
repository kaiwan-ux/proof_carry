# CrossResumeBench v3 — Phase 1 Revision B

## Purpose
Revision B is the corrected native gate before any large v3 benchmark. It tests the **unchanged frozen MCC v2** on one deliberately hard two-world external-effect scenario across LangGraph, CrewAI and Microsoft Agent Framework (MAF).

The research question is narrow and falsifiable:

> When two source executions expose the same transferable evidence but require opposite safe continuation actions, does frozen MCC v2 reject the ambiguous migration and complete both worlds when certified evidence is available?

No LLM or API key is required.

## What is frozen
Revision B does **not** change MCC v2. The following are copied byte-for-byte from the validated v2 package and verified by SHA-256 before every run:

- `frozen_v2/src/crossresumebench_v2/mcc.py`
- `frozen_v2/src/crossresumebench_v2/certificates.py`
- `frozen_v2/src/crossresumebench_v2/models.py`
- `frozen_v2/schemas/mcc_v2.schema.json`

## Two hidden worlds
The portable ambiguous evidence is intentionally identical.

### World A — committed
The external effect really committed, but the response/commit observation is unavailable. Correct continuation: **skip effect**.

### World B — not committed
The external effect did not commit, and the response/commit observation is unavailable. Correct continuation: **execute effect once**.

For `ambiguous_external_commit`, both worlds transfer:

```text
app_state.phase = effect_attempted
history.commit_status = unknown
certificates = []
```

The MCC payload hashes must be byte-identical for the two worlds for each source→target pair. Frozen MCC v2 must reject both.

For `enough_evidence`, an effect-commitment certificate distinguishes `committed` from `not_committed`; MCC should then make opposite correct decisions and complete safely.

## Revision B corrections

### CrewAI
Revision A set `suppress_flow_events=True` while checkpointing was configured to trigger on `method_execution_finished`. CrewAI checkpointing is event-driven, so suppressing Flow events can prevent the checkpoint trigger itself.

Revision B:

1. leaves Flow events enabled;
2. runs the source Flow in a separate Python process;
3. lets `effect_attempt` finish normally;
4. blocks the downstream `ack` listener on an external gate;
5. waits until a real JsonProvider checkpoint file is present;
6. stops the source only **after** the checkpoint is durable.

Native restore is then measured as a control. If CrewAI restore replays the effect, that is recorded as a native-baseline safety failure, not a technical adapter failure.

### Microsoft Agent Framework
Revision A used invalid `WorkflowContext[dict]` annotations. Revision B uses primitive string messages and the official type direction:

- `WorkflowContext[str]` for an executor that sends a string downstream;
- `WorkflowContext[Never, str]` for a terminal executor that yields a string workflow output.

MAF uses `FileCheckpointStorage`, a real `superstep_completed` boundary and resume from `checkpoint_id`.

### Result accounting
Revision B always emits exactly:

- 3 native self-resume control rows;
- 6 native source-capture rows;
- 72 migration rows.

Every migration row has exactly one terminal outcome: safe completion, safe rejection, unsafe violation, or technical failure.

## Experimental matrix

```text
6 directed framework pairs
× 2 hidden worlds
× 2 evidence conditions
× 3 migration methods
= 72 migration rows
```

Framework pairs:

- LangGraph → CrewAI
- LangGraph → MAF
- CrewAI → LangGraph
- CrewAI → MAF
- MAF → LangGraph
- MAF → CrewAI

Methods:

- `mcc_v2` — frozen mechanism under test
- `oracle` — privileged world-truth control
- `explicit_minimal` — privileged explicit-state control

## Expected MCC results if the gate passes

```text
enough_evidence:             12/12 safe completion
ambiguous_external_commit:   12/12 safe rejection
unsafe:                       0
technical failures:           0
```

## Native self-resume control
A framework's own checkpoint restore is reported separately.

- restore completes + ledger correct → safe native self-resume
- restore completes + effect replay/ledger mismatch → unsafe native baseline
- restore API/capture crashes → technical failure

An unsafe native baseline is a scientifically meaningful comparison and does **not** by itself invalidate the MCC cross-runtime experiment. A technical inability to capture/restore does.

## Run on Windows
See `QUICKSTART_WINDOWS.md` or run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionB.ps1
```

At the end, upload:

`CrossResumeBench_v3_Phase1_RevisionB_results.zip`

Whether the gate says PASS or FAIL, send the ZIP. A failed scientific result is still useful evidence.
