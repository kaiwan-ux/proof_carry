# MCC v3 Post-validation Ablation

> **Interpretation:** explanatory post-validation analysis on the already-seen holdout semantics. It is not a second independent validation set.

## Summary

| ablation                     |   safe_completion |   safe_rejection |   unsafe |   rows |
|:-----------------------------|------------------:|-----------------:|---------:|-------:|
| certificates_only            |               342 |              426 |        0 |    768 |
| full_mcc_v3                  |               486 |              282 |        0 |    768 |
| history_only                 |               126 |              642 |        0 |    768 |
| minus_closed_world_gate      |               540 |               54 |      174 |    768 |
| minus_complete_snapshots     |               366 |              402 |        0 |    768 |
| minus_identity_binding       |               414 |              354 |        0 |    768 |
| minus_integrity_verification |               540 |              228 |        0 |    768 |

## Ablation definitions
- `minus_closed_world_gate`: allows fixed-default continuation when the only missing proof is a required fact.
- `minus_integrity_verification`: accepts certificate contents despite bad evidence hashes.
- `minus_identity_binding`: removes semantic identity-binding certificates.
- `minus_complete_snapshots`: removes complete positive/negative snapshot evidence.
- `history_only`: removes all certificates.
- `certificates_only`: removes portable history.

The full mechanism remains frozen and untouched; ablations are implemented in separate study code.
