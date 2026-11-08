# Ablation specification

This is a **post-validation explanatory study**, not an independent holdout. The passed MCC v3 result remains the confirmatory evidence.
The frozen production MCC v3 files are never edited. Each ablation is a study-layer transformation.

Ablations:
1. `full_mcc_v3` — unchanged mechanism.
2. `minus_closed_world_gate` — continue with fixed missing-value defaults when only required facts are unproven.
3. `minus_integrity_verification` — accept attestation content even when its evidence hash is invalid.
4. `minus_identity_binding` — remove identity-binding attestations.
5. `minus_complete_snapshots` — remove closed-world completion/obligation snapshots.
6. `history_only` — remove certificates.
7. `certificates_only` — remove history.

Primary metrics: unsafe count/rate, safe completion coverage, safe rejection rate, family/evidence breakdown.
