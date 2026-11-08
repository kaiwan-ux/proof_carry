# Paper Figure Captions

**Figure 1 — Core mechanism.** Conceptual contrast between MCC v2’s failure mode and MCC v3’s closed-world continuation proof rule. The figure is a mechanism schematic, not the system architecture.

**Figure 2 — Unsafe continuation by method.** Unsafe continuation rates on the sealed holdout. MCC v3 observed 0/768 unsafe continuations; non-privileged reference methods retain substantial unsafe rates.

**Figure 3 — MCC v2 to MCC v3 transition.** Outcome transitions for the same 768 conditions. All 294 MCC v2 unsafe outcomes are resolved by MCC v3: 120 become safe completions and 174 become safe rejections.

**Figure 4 — Ablation.** Removing the closed-world proof gate reintroduces 174 unsafe continuations, while other component removals mainly reduce useful completion coverage. This is the strongest mechanism-level ablation for the core contribution.

**Figure 5 — Statistical safety effect.** Base-case block-bootstrap 95% intervals for the unsafe-rate difference between MCC v3 and each non-privileged comparator. Intervals remain below zero.

**Figure 6 — Evidence behavior.** MCC v3 completes evidence-sufficient, noisy-but-valid, identity-bound, and complete-negative-snapshot cases; it safely rejects missing, tampered, or semantically unbound evidence.

**Figure 7 — Semantic-family behavior.** Outcome composition across eight continuation families; no unsafe MCC v3 continuation was observed in any family.

**Figure 8 — Mechanism latency.** Median and p95 local mechanism latency. MCC v3 increases median processing from about 1.07 ms to 1.35 ms in the measured environment.

**Figure 9 — Payload overhead.** Median and p95 transfer-payload sizes. MCC v3 carries more explicit proof information than MCC v2.

**Figure 10 — Runtime-pair invariance.** All six directed LangGraph/CrewAI/MAF pairs show the same MCC v3 completion/rejection profile and zero unsafe outcomes on the sealed holdout.

**Figure 11 — Security trust boundary.** Security stress test distinguishing in-model integrity corruption from out-of-model authenticated forgery/replay. Hash validation rejects non-rehashed mutations, while forged rehashed or cross-context replayed certificates expose the trusted-witness/context-binding limitation. Do not use this figure to claim cryptographic security.
