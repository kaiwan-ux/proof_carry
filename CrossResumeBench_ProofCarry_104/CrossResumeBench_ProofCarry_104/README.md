# CrossResumeBench ProofCarry-104

A publication-strength follow-up experiment for cross-runtime agent continuation.

## What this package adds

1. **104 independent base cases**: 13 cases in each of 8 workflow families.
2. **Harder semantic states**: committed/not-committed/partially-completed effects, exhausted retries, granted/pending/expired/revoked approvals, failed/pending/completed branches, loop termination, compensation state, callback expiry/wrong-execution, and composites.
3. **Runtime-specific semantic identities**: LangGraph `lg.node::*`, CrewAI `crew.task::*`, and MAF `maf.activity::*`; target contracts use target-native aliases and continuation requires verified identity binding.
4. **Authenticated, context-bound certificates**: Ed25519 signatures bind issuer, execution, case, workflow hash, contract hash, source runtime, target runtime, timestamp, expiry, nonce, fact type, subject, value, and evidence.
5. **Security attacks**: replay, value forgery, recomputed-hash forgery, contract substitution, runtime substitution, expiry, nonce reuse, and unauthorized identity binding.
6. **Always-Reject baseline** to show that safety is not obtained simply by refusing every migration.
7. **Evidence-efficiency measurements**: portable payload bytes plus actual checkpoint-file bytes where available, with serialized pause-metadata bytes reported separately.
8. **Paired end-to-end timing**: capture, evidence construction/signing, proof resolution, serialization, localhost transfer, target runtime resume, parent CPU time, and proof-engine memory.
9. **Ablations retained**: closed-world gate, signature verification, identity binding, complete snapshots, history-only, certificates-only.
10. **Case-level statistics**: the 104 base cases are the independent unit; migration directions, variants, methods, and timing repeats are repeated measurements.

## Important scientific boundary

This package is an **experiment design, not a result**. Do not put expected numbers into the paper until a fresh run has completed and `scripts/verify_results.py` passes. The AAIF/CapLease-named baselines remain independent concept-level references, not official author implementations. The runtime-specific identity labels are a controlled semantic-translation layer attached to real native pause/resume executions; they are not claims about universal public field names in each framework.

## Quick start

### Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH = "$PWD/src;$PWD/frozen_v2/src;$PWD"
python scripts/verify_package.py
python scripts/preflight.py
pytest -q
python scripts/verify_freeze.py
python scripts/run_all.py
python scripts/verify_results.py
```

### Linux/macOS
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
export PYTHONPATH="$PWD/src:$PWD/frozen_v2/src:$PWD"
python scripts/verify_package.py
python scripts/preflight.py
pytest -q
python scripts/verify_freeze.py
python scripts/run_all.py
python scripts/verify_results.py
```

## Run counts

- Semantic scale study: `104 x 5 variants x 6 directions x 10 methods = 31,200` rows.
- Native confirmation: `104 x 6 directions x 3 methods = 1,872` migration rows, plus 312 source captures and 312 self-resume controls.
- Security: `104 x 6 directions x 9 conditions x 2 security methods (ProofCarry and an unkeyed-hash control) = 11,232` rows.
- Ablation: `104 x 6 directions x 4 conditions x 7 configurations = 17,472` rows.
- Performance: `24 stratified cases x 6 directions x 5 repeats x 2 paired methods = 1,440` timed method paths by default; source capture is shared within each pair/repeat.

## Frozen identifiers

- Suite SHA-256: `43129feb6b2f28f7904dee01e3dc92baa9089de34312cd3a9117ddee4c9529ac`
- ProofCarry method-bundle SHA-256: `5900e121047a1a9e293102f5edaa5cd0bd47107a4a312663d8b7d3163cda29cc`

The `results/` directory is intentionally empty in this deliverable. Run the frozen package to generate paper evidence.
