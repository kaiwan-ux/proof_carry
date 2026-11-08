# Claim Boundaries

- Zero unsafe means **zero observed unsafe outcomes under this benchmark**, not a universal proof of safety.
- 104 independent cases strengthen statistical support but do not represent all possible agent workflows.
- AAIF/CapLease references are concept-level independent baselines, not official implementations.
- Localhost transfer is a controlled network-stack measurement, not WAN latency.
- Checkpoint byte counts include only files under a runtime checkpoint directory. LangGraph uses an in-memory saver in this benchmark, so no direct checkpoint-file-size comparison is claimed there; pause metadata is reported separately.
- The benchmark test signing key is public in the codebase for reproducibility and must never be treated as production key management.
