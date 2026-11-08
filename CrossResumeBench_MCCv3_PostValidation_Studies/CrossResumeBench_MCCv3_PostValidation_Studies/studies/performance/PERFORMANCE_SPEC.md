# Performance study

Two levels are separated:

1. **Mechanism microbenchmark (default):** all 768 MCC v3 migration conditions, repeated in memory. Measures payload build, proof resolution/lowering, and payload size. Does not include runtime scheduling.
2. **Native latency (optional but recommended):** 8 canonical enough-evidence cases × 6 directed pairs × 3 repeats. Measures isolated source capture, MCC v3 translation, and target-runtime resume.

Report median and p95 as primary timing statistics. Timing numbers are machine-dependent and should be published with environment metadata. Do not mix them with safety evidence.
