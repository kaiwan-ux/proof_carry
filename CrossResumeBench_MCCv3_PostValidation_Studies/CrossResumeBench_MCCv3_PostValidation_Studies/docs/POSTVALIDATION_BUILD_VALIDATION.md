# Post-validation package build validation

Date: 2026-08-28

The default non-native pipeline was executed end-to-end before packaging with:

- passed-holdout input verification: PASS
- paired statistics: 6,144 raw migration rows, 32 base-case clusters, 5 primary comparators
- ablation: 5,376 rows = 768 conditions × 7 ablations
- full MCC v3 ablation control: 486 safe completions, 282 safe rejections, 0 unsafe
- mechanism microbenchmark: 768 conditions × 10 repeats
- post-validation output verifier: PASS
- unit/structural tests: 4/4 PASS

The optional native-latency script was compiled/static-checked but not executed in the packaging environment because LangGraph/CrewAI/MAF are not installed there. It is intentionally separate from the safety/statistical claims.

## Ablation sanity summary

```csv
ablation,safe_completion,safe_rejection,unsafe,rows
certificates_only,342,426,0,768
full_mcc_v3,486,282,0,768
history_only,126,642,0,768
minus_closed_world_gate,540,54,174,768
minus_complete_snapshots,366,402,0,768
minus_identity_binding,414,354,0,768
minus_integrity_verification,540,228,0,768
```

## Statistical sanity excerpt

# Paired Statistical Validation

Primary clustering unit: **base case (n=32)**, not individual migration rows.

## MCC v3 holdout estimate
- Safe completion: 486/768 (63.28%)
- Unsafe: 0/768 (0.00%)
- Wilson 95% CI for unsafe rate: 0.000% to 0.498%

## Microbenchmark sanity excerpt

# Mechanism Microbenchmark

Instances per repeat: 768; repeats: 10.

| Stage | Median (µs) | p95 (µs) | Mean (µs) |
|---|---:|---:|---:|
| mcc_v3_build | 160.54 | 270.94 | 168.63 |
| mcc_v3_resolve | 166.70 | 287.03 | 174.40 |
| mcc_v3_lower_total | 330.18 | 564.16 | 344.94 |
| mcc_v2_total | 235.58 | 432.81 | 253.10 |

## Payload bytes
- MCC v3 median: 1004 B
- MCC v2 median: 483 B

Timing is mechanism-only and excludes native runtime scheduling/network/tool latency.

Timing values above are packaging-environment sanity checks only; users should report timings from their own measured environment.
