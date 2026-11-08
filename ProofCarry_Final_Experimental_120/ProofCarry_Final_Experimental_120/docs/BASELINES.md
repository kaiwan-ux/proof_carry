# Baselines and Controls

- **ProofCarry**: authenticated evidence + identity binding + complete snapshots + dependency reasoning + closed-world proof gate.
- **MCC v2 frozen-style reference**: schema-strict history/certificate reconstruction without the general v3 closed-world continuation contract.
- **History-only**: optimistic history replay; absent continuation obligations are not certified.
- **AAIF reference**: independent concept-level checkpoint/state portability reference used for controlled comparison. It is not an official AAIF implementation.
- **CapLease reference**: independent concept-level durable-effect reference. It is not an official CapLease implementation.
- **AAIF + CapLease reference**: combination of the two concept-level references.
- **Always Reject**: zero-unsafe / zero-useful-completion control for detecting trivial refusal.
- **Oracle**: privileged upper-bound control with hidden truth; not a deployable competitor.

Never describe the concept-level references as authoritative implementations from the original authors.
