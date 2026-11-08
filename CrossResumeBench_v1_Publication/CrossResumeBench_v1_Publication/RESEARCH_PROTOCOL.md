# Research protocol

## RQ1 — Cross-runtime continuation
Can a fixed MCC mechanism preserve observable workflow behavior across heterogeneous runtime targets on unseen semantic-mismatch cases?

## RQ2 — Information boundary
Which failures are reconstructable from portable semantic history, and which require external certified evidence?

## RQ3 — Competing representations
How do MCC, state/history baselines, an AAIF-style state projection, a CapLease-inspired effect ledger, their combination, explicit minimal state, and a semantic oracle compare on safe completion, safe rejection, unsafe continuation, and payload size?

## Primary metrics
- Safe Completion Coverage (SCC)
- Safe Rejection Rate (SRR)
- Unsafe Continuation Rate (UCR)
- Duplicate External Effects
- Completed-Step Replay
- Payload bytes
- Technical failure rate

## Frozen-evaluation policy
The MCC mechanism must be frozen before the benchmark suite. If the mechanism changes after observing results, create v2 and regenerate a new independently seeded hold-out suite.

## Kill criteria
The paper's MCC novelty is weakened if: (a) `aaif_plus_caplease` matches MCC across the full frozen suite with equal safety/coverage, (b) history inference alone matches MCC without materially more rejection, or (c) native results depend on a single framework pair. Report such outcomes rather than hiding them.
