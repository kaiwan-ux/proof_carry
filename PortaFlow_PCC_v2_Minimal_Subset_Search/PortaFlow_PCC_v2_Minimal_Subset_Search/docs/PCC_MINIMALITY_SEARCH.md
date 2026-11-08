# Minimality Search Algorithm
Let component vocabulary be C with |C|=6. Enumerate every subset S⊆C.

For each subset, evaluate two execution semantics:

**Explicit(S):** only the semantic fields physically present in S may be used.

**Hybrid(S):** if history∈S, a deterministic reconstruction algorithm may infer missing progress/frontier/obligation/contract facts from history plus static workflow structure. A critical external commitment with multiple histories-compatible states is not guessed; migration is rejected unless S supplies sufficient certified evidence.

A candidate is admissible for minimal full coverage iff:

`safe_completions = 8`, `rejections = 0`, `unsafe_violations = 0`.

Among admissible candidates choose smallest |S|, then smallest mean semantic payload bytes. The native stage verifies that this mechanism-level result survives real runtime adapters.
