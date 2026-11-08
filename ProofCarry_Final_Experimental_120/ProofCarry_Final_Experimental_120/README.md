# ProofCarry Final Experimental Package (120 Unique Cases)

This package is the final experimental scaffold for **ProofCarry / MCC v3**, a proof-carrying mechanism for safe continuation across heterogeneous agent runtimes.

## What is included

1. **Original sealed 32-case holdout evidence** preserved read-only under `legacy_evidence/sealed_holdout_32/` (6,144 migration rows). It is re-analyzed, not silently regenerated.
2. **Expanded120 semantic benchmark:** 8 workflow families x 15 genuinely distinct scenario concepts = 120 base cases.
3. **Seven evidence/challenge conditions** across all six directed runtime pairs.
4. **Runtime-specific identity experiment:** correct, missing, wrong, and ambiguous source-to-target mappings.
5. **Authenticated security experiment:** HMAC-SHA256 test certificates vs an unkeyed hash-only control; nine required attacks plus valid controls.
6. **Ablation study:** closed-world gate, authentication, identity binding, complete snapshots, dependency reasoning, and certificate verification.
7. **Always Reject control** to demonstrate selective safety rather than trivial refusal.
8. **End-to-end semantic migration performance:** capture, evidence construction/signing, serialization, transfer, verification/parsing, proof, translation, semantic resume check, and payload sizes with repeated measurements.
9. **Native-runtime status/protocol:** native results are never inferred from labels or dependency presence. The new expanded native benchmark remains NOT_RUN until actual framework APIs execute successfully. Prior native evidence is preserved separately.
10. **One-command reproducibility:** `python reproduce_all.py`.

## Important scientific boundary

The new 120-case benchmark is a designed semantic benchmark. It is **not** an independent real-world workload corpus. Results from it must be described as applying *under the evaluated benchmark conditions*. The concept-level AAIF and CapLease baselines in this package are experimental references, **not official implementations**.

The default certificate authenticator uses **HMAC-SHA256 with a deterministic test-only key** for reproducibility. This is suitable for evaluating authentication/replay logic but is not a production PKI design.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/audit_cases.py --root .
python scripts/verify_legacy.py
python reproduce_all.py --native-status
```

For a faster performance smoke run:

```bash
python reproduce_all.py --performance-reps 3 --performance-warmups 1 --performance-max-cases 8 --native-status
```

## Raw-data policy

Every run creates a new directory:

`results/raw/<run_id>/`

The runner refuses to overwrite an existing run directory. Derived outputs are written to `results/processed/<run_id>/`; publication-facing latest tables/figures are regenerated under `results/tables/` and `results/figures/`.

## Families

- Effect commitment
- Retry
- Approval
- Parallel
- Loop
- Compensation
- Callback
- Composite

Each contains exactly 15 distinct scenario concepts. See `benchmark/cases/case_catalog.csv` and `docs/CASE_DESIGN_NOTES.md`.

## Native evaluation

Run:

```bash
python native/run_native_validation.py --root . --out results/native/native_validation.csv
```

This command is intentionally conservative. It reports dependencies/status and does **not** call a framework "validated" merely because it imports. Follow `docs/NATIVE_VALIDATION_PROTOCOL.md` to add/execute pinned framework-specific adapters. Existing passed 32-case native evidence is in `legacy_evidence/sealed_holdout_32/`.
