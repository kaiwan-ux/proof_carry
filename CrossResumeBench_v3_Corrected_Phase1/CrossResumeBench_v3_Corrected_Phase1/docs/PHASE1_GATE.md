# Phase-1 GO/NO-GO Gate

`go_for_full_v3=true` only if all mandatory checks pass:

1. Frozen MCC v2 verification succeeds.
2. Runtime capability probes succeed for all installed target versions.
3. The common checkpoint is real and same-runtime self-resume succeeds in LangGraph, CrewAI, and MAF.
4. Native source artifact proves `ack` is still pending at the selected checkpoint.
5. MCC enough-evidence: 6/6 directed pairs safe, zero duplicate effect.
6. MCC ambiguous-commit: 6/6 directed pairs reject before target starts.
7. No MCC payload contains forbidden derived/native checkpoint fields.
8. Target adapters execute their own native `ack -> finish` control flow.
9. Result verification has zero technical failures for mandatory Phase-1 rows.

If any gate fails, do not edit MCC v2. First classify the failure as runtime capability, extractor/resumer defect, invalid pause point, or MCC limitation.
