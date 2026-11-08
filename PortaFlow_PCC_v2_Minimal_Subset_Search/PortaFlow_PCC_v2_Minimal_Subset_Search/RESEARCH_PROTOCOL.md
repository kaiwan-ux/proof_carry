# Research Protocol — Minimal Certified Continuation

## Research question
Which subset of framework-neutral continuation semantics is sufficient for safe cross-runtime continuation, and how much explicit information can be replaced by verified reconstruction from portable history plus static workflow structure?

## Hypotheses
- **H1:** At least one strict subset of PCC v1 will match full PCC safe-completion coverage on the hold-out suite.
- **H2:** Hybrid reconstruction will require fewer stored component families than an explicit-only representation.
- **H3:** Ambiguous external-effect commitment will require explicit certified evidence or safe rejection.

## Stage A
Exhaust all 2^6 = 64 subsets under explicit and hybrid modes. For each workflow report safe completion, safe rejection, unsafe continuation, capsule bytes and failure types.

A subset is **full-coverage safe** only if all eight workflows safely complete, with zero rejections and zero unsafe violations.

The minimal subset is chosen lexicographically by:
1. full safe completion,
2. zero rejection,
3. zero unsafe violation,
4. fewest stored component families,
5. smallest mean serialized semantic payload.

## Stage B
Confirm the discovered candidates on real LangGraph/CrewAI/MAF source and target executions for all six directed framework pairs. Candidate selection is produced by Stage A, not hard-coded.

## Falsification / pivot rules
- If no strict subset matches full PCC, retain full PCC.
- If history-only hybrid inference safely completes nearly all cases with negligible rejection, explicit PCC is over-specified; pivot toward verified reconstruction.
- If a very small subset (e.g. history + receipts) matches full PCC natively, simplify PortaFlow around that representation.
- If Stage-A candidate fails native confirmation, do not claim minimality; investigate framework-specific hidden semantics.

## Claim boundary
This experiment can establish **empirical minimality on this benchmark/component vocabulary**, not universal minimality across all possible agent runtimes or workflows.
