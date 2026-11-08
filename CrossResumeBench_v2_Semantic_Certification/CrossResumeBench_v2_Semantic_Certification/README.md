# CrossResumeBench v2 — Semantic Certification & Real Source Capture

This package is the corrected successor to CrossResumeBench v1. It was created after v1 exposed four publication-critical issues: MCC carried derived state despite a history+receipts specification; effect receipts did not prove enclosing semantic completion; source-framework labels did not affect source extraction; and the AAIF+CapLease reference baseline reused MCC reconstruction logic.

## What v2 changes

1. **MCC v2 is schema-strict.** It transports only `app_state + history + certificates`; target reconstruction happens after transfer. Hidden reconstructed state is rejected.
2. **General semantic certificates.** External-effect commitment and semantic-unit completion are distinct facts. MCC rejects unknown semantic progress instead of replaying it.
3. **Real source adapter interface.** Native confirmation calls the source runtime first (`capture_source`) and stores a source-native artifact before translating to a different target runtime.
4. **Independent baselines.** History, AAIF-style, and CapLease-style reference baselines have separate code paths and do not call MCC reconstruction.
5. **Brand-new frozen suite.** 70 cases across 14 new semantic-mismatch families. The mechanism hash is recorded before the suite freeze record.

## Evidence layers

- Stage A: 70 cases × 10 conditions = **700 deterministic semantic evaluations**.
- Stage B: 14 canonical cases × 6 directed framework pairs × 7 conditions = **588 native confirmation executions**, plus 42 native source captures (14 × 3 frameworks).

No LLM or API key is required.

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.un_crossresumebench_v2.ps1
```

Upload `CrossResumeBench_v2_results.zip` after it completes.

## Important claim boundary
The native layer now invokes the source framework and target framework separately, but the deterministic benchmark actions are still common benchmark tasks. This tests native capture/translation/lowering infrastructure and semantic preservation; it is not arbitrary Python process migration or direct binary checkpoint interchange.

## Hold-out variants are materially different
Each family has five evidence conditions rather than five renamed copies: certificate available; semantic completion observable in history; semantic-completion certificate unavailable; effect commit observable in history with no receipt; and ambiguous effect with no receipt. This allows the frozen mechanism to complete some migrations and safely reject genuinely under-evidenced ones.
