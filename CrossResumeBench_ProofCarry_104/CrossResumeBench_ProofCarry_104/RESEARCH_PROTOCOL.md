# Research Protocol

## RQ1 — Useful safety
Does ProofCarry obtain zero observed unsafe continuations while completing cases with sufficient evidence, unlike Always Reject which is safe but has zero coverage?

## RQ2 — Cross-runtime identity
Does verified identity binding allow continuation across runtime-specific identifiers, and does missing binding cause safe rejection?

## RQ3 — Security
Do Ed25519 context-bound certificates reject replay, forgery, contract/runtime substitution, expiry, nonce reuse, and unauthorized semantic bindings?

## RQ4 — Mechanism attribution
Which components are responsible for safety/coverage? Evaluate full ProofCarry against six ablations.

## RQ5 — Practical overhead
What are end-to-end latency, proof latency, payload bytes, source native artifact bytes, parent CPU time, and decode-memory overhead?

## Statistics
Primary independent unit: 104 base cases. Use case-block bootstrap confidence intervals and paired case-level tests; do not treat runtime directions or variants as independent samples.
