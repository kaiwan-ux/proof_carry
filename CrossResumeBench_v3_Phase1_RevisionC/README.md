# CrossResumeBench v3 — Phase 1 Revision C

## Purpose
Revision C is a **MAF-only adapter correction** after Revision B established that LangGraph ↔ CrewAI works bidirectionally with the frozen MCC v2 mechanism. It does not redesign the research mechanism or the two-world experiment.

The question remains:

> When two source executions expose the same transferable evidence but require opposite safe continuation actions, does frozen MCC v2 reject the ambiguous migration and complete both worlds when certified evidence is available?

No LLM or API key is required.

## What is frozen
Revision C does **not** change MCC v2. These files are copied byte-for-byte from the validated v2 package and verified by SHA-256 before every run:

- `frozen_v2/src/crossresumebench_v2/mcc.py`
- `frozen_v2/src/crossresumebench_v2/certificates.py`
- `frozen_v2/src/crossresumebench_v2/models.py`
- `frozen_v2/schemas/mcc_v2.schema.json`

Revision C also keeps the Revision-B LangGraph adapter, CrewAI adapter, two hidden worlds, evidence variants, safety oracle, privileged controls and 72-row matrix unchanged.

## The only runtime change: Microsoft Agent Framework
Revision B failed because MAF rejected locally-scoped/postponed `WorkflowContext[...]` annotations during handler introspection.

Revision C uses the framework's explicit handler declaration mode instead:

```python
@handler(input=str, output=str)
```

for executors that forward a message, and:

```python
@handler(input=str, workflow_output=str)
```

for the terminal executor. When explicit types are supplied, handler type introspection is disabled.

For checkpoint capture, Revision C:

1. builds the workflow with `FileCheckpointStorage`;
2. runs until `superstep_completed` after `effect_attempt`;
3. stops immediately at that documented checkpoint-safe boundary;
4. gets the durable checkpoint using `storage.get_latest(workflow_name=...)`;
5. verifies that `ack_count == 0` and `finish_count == 0`;
6. rebuilds the same workflow and resumes from `checkpoint_id`.

## New MAF-only pre-gate
Before the full 72-row matrix is allowed to run, Revision C executes:

```text
python scripts/probe_maf_revisionC.py
```

It independently verifies:

- MAF capability imports;
- committed native self-resume;
- committed source capture before ack;
- not-committed source capture before ack;
- target `committed` → `skip_effect`;
- target `not_committed` → `execute_effect`.

If this probe fails, the experiment **stops before the 72-row grid** and exports:

```text
CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip
```

Send that diagnostic ZIP instead of trying to continue manually.

## Two hidden worlds

### World A — committed
The external effect really committed, but the commit observation is unavailable. Correct continuation: **skip effect**.

### World B — not committed
The effect did not commit and the commit observation is unavailable. Correct continuation: **execute effect once**.

For `ambiguous_external_commit`, both worlds transfer the same portable evidence:

```text
app_state.phase = effect_attempted
history.commit_status = unknown
certificates = []
```

The MCC payload hashes must be byte-identical for the two worlds for each source→target pair, and frozen MCC v2 must reject both.

For `enough_evidence`, a typed effect-commitment certificate distinguishes the worlds. MCC must then make opposite correct decisions and complete safely.

## Full Phase-1 matrix after the MAF probe passes

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

## Pass target

```text
MAF pre-gate: PASS
3/3 native restores technically executable
6/6 source captures successful
72/72 migration rows present
0 migration technical failures

MCC enough_evidence:            12/12 safe completion
MCC ambiguous_external_commit:  12/12 safe rejection
MCC unsafe:                      0

6/6 ambiguous pair hashes identical across worlds
6/6 certified pairs make opposite correct decisions
48/48 privileged controls safe
```

Native self-resume safety is a separate control result: a runtime may restore but replay an effect; that is an unsafe native baseline, not an MCC failure. Native restore must nevertheless be technically executable.

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionC.ps1
```

### What to upload
If the MAF pre-gate fails, upload:

```text
CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip
```

If the MAF pre-gate passes and the full run executes, upload:

```text
CrossResumeBench_v3_Phase1_RevisionC_results.zip
```

Upload the generated ZIP whether the scientific gate says PASS or FAIL.
