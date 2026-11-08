# Claim Boundaries

Safe wording after a successful deterministic run:
- "ProofCarry observed zero unsafe continuations on the evaluated benchmark" — only if generated raw data show zero.
- "The closed-world gate is associated with the measured safety difference in the ablation" — report generated values and statistics.
- "Behavior was invariant across six semantic runtime-pair representations" — only for semantic mapping tests.

Do not claim:
- universal cross-runtime interoperability;
- official superiority over AAIF or CapLease (the included versions are concept-level references);
- production cryptographic security from the test HMAC protocol;
- native validation of a framework unless `native_validation.csv` contains actual executed evidence;
- real-world generalization from synthetic semantic cases alone.
