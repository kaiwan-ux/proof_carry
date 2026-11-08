# Paired Statistical Validation

Primary clustering unit: **base case (n=32)**, not individual migration rows.

## MCC v3 holdout estimate
- Safe completion: 486/768 (63.28%)
- Unsafe: 0/768 (0.00%)
- Wilson 95% CI for unsafe rate: 0.000% to 0.498%

## Paired comparisons
### MCC v3 vs mcc_v2_frozen
- Unsafe-rate difference: -38.28 percentage points (MCC v3 - comparator)
- Case-block bootstrap 95% CI: -50.78 to -26.56 pp
- Case-level Wilcoxon Holm-adjusted p: 6.88184e-05
- Safe-completion-rate difference: 8.59 pp
- Completion block-bootstrap 95% CI: -2.34 to 20.31 pp

### MCC v3 vs history_inference
- Unsafe-rate difference: -47.66 percentage points (MCC v3 - comparator)
- Case-block bootstrap 95% CI: -60.94 to -34.38 pp
- Case-level Wilcoxon Holm-adjusted p: 6.88184e-05
- Safe-completion-rate difference: 10.94 pp
- Completion block-bootstrap 95% CI: -3.12 to 25.00 pp

### MCC v3 vs aaif_reference
- Unsafe-rate difference: -30.47 percentage points (MCC v3 - comparator)
- Case-block bootstrap 95% CI: -42.97 to -18.75 pp
- Case-level Wilcoxon Holm-adjusted p: 0.000160949
- Safe-completion-rate difference: 25.00 pp
- Completion block-bootstrap 95% CI: 11.72 to 38.28 pp

### MCC v3 vs caplease_reference
- Unsafe-rate difference: -39.84 percentage points (MCC v3 - comparator)
- Case-block bootstrap 95% CI: -52.34 to -28.12 pp
- Case-level Wilcoxon Holm-adjusted p: 6.88184e-05
- Safe-completion-rate difference: 3.12 pp
- Completion block-bootstrap 95% CI: -9.38 to 16.41 pp

### MCC v3 vs aaif_plus_caplease_reference
- Unsafe-rate difference: -39.84 percentage points (MCC v3 - comparator)
- Case-block bootstrap 95% CI: -52.34 to -28.12 pp
- Case-level Wilcoxon Holm-adjusted p: 6.88184e-05
- Safe-completion-rate difference: 3.12 pp
- Completion block-bootstrap 95% CI: -9.38 to 16.41 pp

## Interpretation boundary
These tests quantify the completed benchmark. Base-case block bootstrap/Wilcoxon are primary to reduce pseudo-replication; row-level McNemar tests are supplementary. Statistical significance does not establish external generalization beyond this benchmark.
