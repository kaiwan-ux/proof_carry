# NativeFull Experimental Protocol

## Research question

Does ProofCarry retain its fail-closed continuation behavior when source checkpoints and target continuation are exercised through actual LangGraph, CrewAI, and Microsoft Agent Framework runtimes rather than runtime labels alone?

## Separation from semantic evaluation

NativeFull is an additional evidence layer. Semantic rows are not rewritten or upgraded to native rows. Native results have their own CSVs and verdict.

## Stages

### N0 — Environment doctor

Record Python/platform, framework versions, import success, and checkpoint/resume capability surface.

### N1 — Native family gate

For one representative from each of eight workflow families, run actual checkpoint + self-resume in each framework. 24 rows total.

### N2 — Self-resume controls

For every selected case and framework, capture a real paused execution and resume it in the same framework. Failure to return from the lifecycle is diagnostic/technical even if semantic state happens to reach the expected state.

### N3 — Source native capture

For every selected case and source framework, capture the persisted/native pause and record checkpoint reference, checkpoint byte size when observable, portable pause metadata size, and errors.

### N4 — Directed cross-runtime matrix

For every selected case, all six source->target pairs, all requested evidence conditions, and all requested methods:

1. reuse a successful source-native pause;
2. generate the corresponding portable evidence condition;
3. run the selected admission method;
4. if rejected, record safe rejection and do not execute target runtime;
5. if continued, seed the portable source semantic store and execute the lowered plan through the target runtime;
6. compare final semantic state to the oracle state;
7. record completion/rejection/unsafe/technical plus latency and payload.

### N5 — Analysis / verification

Aggregate by method, pair, family, and condition. Verify exact row counts, unique run IDs, mutually exclusive outcomes, and that technical failures are never counted as safety outcomes.

## Case presets

- `smoke8`: 1/family
- `smoke24`: 3/family
- `paper104`: 13/family = 104
- `all120`: 15/family = 120

## Method profiles

- `proofcarry`: ProofCarry only
- `core`: ProofCarry, ProofCarry-no-auth, history-only, always-reject
- `full`: ten methods from the frozen benchmark package

## Claim gates

- `THREE_RUNTIME_NATIVE_MATRIX` only if all framework/family gates pass and the evaluated matrix has no technical failures.
- Otherwise report `PARTIAL_NATIVE_REPRODUCIBILITY` and state exactly which pairs/families ran.
- Zero observed unsafe rows is never described as a universal guarantee.
- AAIF/CapLease references remain concept-level implementations, not official artifacts.
