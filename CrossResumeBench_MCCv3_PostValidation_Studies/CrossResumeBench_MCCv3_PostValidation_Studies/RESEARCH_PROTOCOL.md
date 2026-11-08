# Research Protocol

1. Verify passed-holdout input hashes and the passed research gate.
2. Run paired statistical analysis without changing any experimental rows.
3. Run ablations in a separate study namespace; never overwrite frozen MCC v3.
4. Run mechanism microbenchmark with warmups and repeated timings.
5. Optionally run native timing; report hardware/software environment and do not interpret latency as safety evidence.
6. Preserve all raw outputs and export them with the read-only input hash record.

### Claims allowed after this package

- Paired benchmark effect sizes and confidence intervals.
- Component-importance observations from post-validation ablation.
- Measured payload/timing overhead on the reported environment.

### Claims not allowed from this package alone

- New independent generalization evidence from the ablation study.
- Universal superiority to AAIF/CapLease; those remain independent concept-level references.
- Cryptographic security; current attestations remain trusted-witness hash evidence unless separately upgraded/tested.
