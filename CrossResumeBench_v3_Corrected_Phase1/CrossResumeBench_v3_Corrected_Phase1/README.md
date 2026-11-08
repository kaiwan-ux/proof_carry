# CrossResumeBench v3 — Corrected Phase-1 Native Gate

This package is the corrected successor to the original v3 planning folder.
It does **not** jump directly to a 6,720-row benchmark. It first validates the research premise with a strict native gate.

## Research question
Can the **frozen MCC v2** evidence format (`app_state + history + certificates`) translate a genuinely paused in-flight execution from one agent runtime to another without replaying an already-committed external effect?

## What is corrected
1. **MAF means Microsoft Agent Framework**, implemented with `agent_framework` — never AutoGen.
2. Native self-resume is a **separate prerequisite control**, not multiplied as a cross-framework migration baseline.
3. Pause points are classified as `native_checkpointable`, `externally_blocked_capturable`, or `unsupported_at_this_boundary`.
4. Evidence variants are applied only where semantically meaningful.
5. MCC v2 is copied byte-for-byte from the v2 package and verified before every run.
6. The Phase-1 gate uses real native checkpoint/resume mechanisms and no shared target continuation engine.
7. Results cannot be exported unless all mandatory gate checks pass.

## Phase-1 case
`effect_committed_ack_pending`

Source runtime:
1. commit an external effect exactly once;
2. reach a real runtime checkpoint with acknowledgment still pending;
3. capture native checkpoint metadata;
4. extract MCC v2 evidence.

Target runtime:
1. reconstruct only from the frozen MCC v2 payload;
2. reject if commit evidence is ambiguous;
3. otherwise continue through the target runtime's own `ack -> finish` control flow;
4. verify the external effect was not executed twice.

### Evidence variants
- `enough_evidence` — certified commit + semantic completion; should continue.
- `ambiguous_external_commit` — commit result is not provable; MCC must reject before target execution.

## Frameworks
- LangGraph 1.2.11
- CrewAI 1.15.17
- Microsoft Agent Framework (`agent-framework-core`) 1.15.0

## Phase-1 cross-framework matrix
All six directed pairs are tested for MCC v2. Oracle and explicit-minimal are smoke controls.
Native self-resume is run separately once per framework.

## Run
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:CREWAI_TRACING_ENABLED="false"
$env:CREWAI_DISABLE_TELEMETRY="true"
$env:OTEL_SDK_DISABLED="true"
.\run_phase1.ps1
```

Expected output:
- `results/PHASE1_GATE.json`
- `results/phase1_runs.csv`
- `results/self_resume.csv`
- `CrossResumeBench_v3_Phase1_results.zip`

## GO rule
Do **not** implement the full v3 benchmark until `PHASE1_GATE.json` says `go_for_full_v3: true`.
