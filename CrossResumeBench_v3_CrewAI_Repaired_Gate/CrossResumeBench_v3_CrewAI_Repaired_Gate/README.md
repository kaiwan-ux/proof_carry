
# CrossResumeBench v3 — CrewAI Repaired Gate

## Purpose
This is a **CrewAI-only** native gate extracted from the validated Phase-1 Revision-C design. It contains no LangGraph runtime and no Microsoft Agent Framework runtime.

It answers one narrow question:

> Is the repaired CrewAI checkpoint/capture/resume path technically sound enough to support the two-world continuation experiment, while frozen MCC v2 completes certified cases and rejects indistinguishable ambiguous cases?

No LLM and no API key are required.

## Why this CrewAI repair exists
The earlier CrewAI gate failed because `method_execution_finished` checkpoint persistence raced with an exception-based pause. The repaired adapter:

1. keeps CrewAI Flow events enabled;
2. runs the source Flow in a child process;
3. completes `effect_attempt`;
4. blocks the downstream `ack` listener on an external file gate;
5. waits for a real persisted `JsonProvider` checkpoint;
6. verifies the ledger is still before ACK/finish;
7. only then stops the source process.

This is the CrewAI adapter used by successful Phase-1 Revision C.

## Experiment
Two hidden worlds share the same portable uncertain history:

- `committed`: external effect already happened; safe target action is `skip_effect`.
- `not_committed`: external effect did not happen; safe target action is `execute_effect` once.

Two evidence conditions:

- `enough_evidence`: an effect-commitment certificate reveals the correct world.
- `ambiguous_external_commit`: no certificate; both MCC payloads must be byte-identical and must be rejected.

Three methods:

- `mcc_v2` — frozen mechanism under test.
- `oracle` — privileged world-truth control.
- `explicit_minimal` — privileged explicit-state control.

Focused matrix:

```text
CrewAI -> CrewAI
2 worlds x 2 evidence conditions x 3 methods = 12 migration rows
```

The package also runs one native self-resume control and two independent source captures.

## PASS target

```text
CrewAI capability probe: ready
Native self-resume: technically restorable
Committed source capture: effect=1, ack=0, finish=0
Not-committed source capture: effect=0, ack=0, finish=0
12/12 migration rows present
0 technical migration failures
0 unsafe migrations
MCC enough_evidence: 2/2 safe completion
MCC ambiguous_external_commit: 2/2 safe rejection
Ambiguous MCC payload hashes: identical across worlds
Certified worlds: committed -> skip_effect; not_committed -> execute_effect
Privileged controls: 8/8 safe
```

Native self-resume safety is reported separately. The infrastructure gate requires technical restorability; a native replay issue is a baseline/runtime result, not permission to modify frozen MCC v2.

## Windows run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_crewai_gate.ps1
```

## Outputs
On a completed run:

- `results/CREWAI_REPAIR_PROBE.json`
- `results/self_resume.csv`
- `results/source_capture_results.csv`
- `results/crewai_gate_runs.csv`
- `results/CREWAI_REPAIRED_GATE.json`
- `results/ANALYSIS_SUMMARY.md`
- `CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip`

If the native repair probe fails before the matrix, the package exports:

- `CrossResumeBench_v3_CrewAI_Repaired_Gate_diagnostics.zip`

## Scientific rule
Do **not** modify frozen MCC v2 because of a CrewAI adapter failure. A native integration failure is diagnosed as an infrastructure/runtime result. Any future MCC mechanism change must be separately versioned and evaluated on new held-out evidence.
