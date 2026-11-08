# Mechanism Microbenchmark

Instances per repeat: 768; repeats: 10.

| Stage | Median (µs) | p95 (µs) | Mean (µs) |
|---|---:|---:|---:|
| mcc_v3_build | 642.60 | 3078.40 | 988.57 |
| mcc_v3_resolve | 661.85 | 3377.50 | 1082.27 |
| mcc_v3_lower_total | 1347.30 | 5576.10 | 2077.90 |
| mcc_v2_total | 1066.70 | 4831.10 | 1720.66 |

## Payload bytes
- MCC v3 median: 1004 B
- MCC v2 median: 483 B

Timing is mechanism-only and excludes native runtime scheduling/network/tool latency.
