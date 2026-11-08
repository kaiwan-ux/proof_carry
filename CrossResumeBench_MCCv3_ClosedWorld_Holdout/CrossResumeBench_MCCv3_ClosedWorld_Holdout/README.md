# CrossResumeBench — MCC v3 Closed-World Holdout

This package is the **fresh validation stage after the frozen MCC v2 full-v3 discovery result exposed 192 unsafe continuations / 480 MCC evaluations**.

## Mechanism
MCC v3 adds a target-side **Continuation Proof Contract**. The transfer payload still contains portable app state, history and attestations; it does **not** contain evaluator truth or native checkpoint state. The target verifies the public contract hash, resolves every continuation-critical fact, and rejects if any required fact is missing, conflicting, tampered, or uses an unbound semantic identity.

Core rule: **prove every fact that can change the safe next action; otherwise reject.**

## Discovery / holdout separation
- Prior discovery ZIP SHA-256: `163aa4414b05cbde2c46e46076b8ece4c01e31f695e032924128d00e20af9f18`
- MCC v3 mechanism frozen SHA-256: `4e6fdd6d0fc949a7e337b02be9d71706a40f5fc87971f8030e0a5a02a32f6194`
- Only after that freeze was the 32-case holdout seed generated.
- Holdout suite SHA-256: `3cc06e8817f1b1861381ec348bbcf769be4b169833b9b24deccfc688a154f8e8`

The holdout has 32 fresh base cases, including 4 composite cases, 128 case×evidence instances, 6 directed runtime pairs and 8 methods = **6,144 migrations**.

## Primary success gate
MCC v3 must have **0 unsafe**, **0 technical**, and match every preregistered holdout expectation. Native self-resume and source capture must be 96/96.

Do not modify the mechanism or holdout after seeing results. A failure is a research result.
