# CrossResumeBench v3 — Phase1 Revision A

This is the corrected Phase-1 gate for **true mid-execution cross-runtime continuation**. It exists because the previous Phase-1 run exposed adapter bugs, incomplete row accounting, provenance leakage, and an invalid ambiguity test.

## Research question

Can the **frozen MCC v2** safely distinguish what can be continued from what must be rejected when two real source executions expose the **same portable uncertain evidence** but require opposite external-effect decisions?

## The two-world experiment

The source pauses after an external-effect attempt and before acknowledgment.

- **World A — committed:** external effect really happened (`effect_count=1`).
- **World B — not_committed:** external effect did not happen (`effect_count=0`).

For the `ambiguous_external_commit` variant, both worlds transfer exactly the same:

```text
app_state: phase=effect_attempted
history: effect attempted, commit_status=unknown
certificates: []
```

For the same source/target pair, the two MCC payloads **must be byte-identical**. Correct continuation nevertheless differs: World A must skip the effect, World B must execute it. Therefore a safe evidence-only mechanism must reject both when no certified commitment fact is available.

## Matrix

- 3 native self-resume controls (committed world)
- 6 source captures (3 frameworks × 2 hidden worlds)
- 72 migration rows = 6 directed pairs × 2 worlds × 2 evidence variants × 3 methods
- MCC v2 contributes 24 rows: 12 certified completions + 12 expected safe rejections

Frameworks: LangGraph, CrewAI, **Microsoft Agent Framework (MAF)**.

## What was corrected

1. MCC v2 remains byte-for-byte frozen.
2. Neutral `phase=effect_attempted`; no `effect_committed` leak.
3. Target continuation includes a real `effect_guard`, so ambiguous commit status is decision-relevant.
4. Target ledgers are cloned from evaluator-only external-world truth; target control code does **not** read ledger truth to choose skip/execute.
5. CrewAI state-class closure bug removed; source stops after a native method checkpoint and before ack.
6. MAF uses one async path and stops on a real `superstep_completed` checkpoint; no nested `asyncio.run()`.
7. `source_runtime` provenance is preserved via `native_observation.framework`.
8. Every planned migration row is emitted even when a source adapter fails. Exact expected migration row count is 72.
9. Scientific gate failure does not suppress the results ZIP. A structurally complete failed run is still exportable for diagnosis.
10. Full v3 remains disabled until this gate passes.

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionA.ps1
```

No LLM and no API key are required.

At the end, upload:

`CrossResumeBench_v3_Phase1_RevisionA_results.zip`

Whether the gate says PASS or FAIL, upload that ZIP for analysis.
