# Research Protocol — CrossResumeBench v2

## Primary RQ
Can a schema-strict evidence-transfer mechanism preserve or safely reject in-flight workflow continuation across heterogeneous runtimes when source and target execution granularities disagree?

## Secondary RQs
- When does external-effect evidence fail to establish semantic progress?
- Do semantic-completion certificates recover coverage without transferring source-native checkpoints?
- Does the result survive real source-runtime extraction rather than source labels?
- How does MCC v2 compare with independent history, AAIF-style, CapLease-style, explicit-minimal and oracle baselines?

## Frozen-evaluation policy
MCC v2 mechanism/schema/certificate code is hashed first. The v2 suite is then generated and frozen separately. After observing results, do not edit either frozen asset; create v3 with a new seed and suite.

## Kill criteria
- MCC v2 has unsafe continuations on held-out cases.
- Independent AAIF+CapLease reference matches or exceeds MCC v2 with lower/equal overhead and no extra rejection.
- Source framework does not materially enter the native capture path.
- MCC payload contains any derived continuation state or native checkpoint blob.
- Results require one framework pair to look good.

## Metrics
Safe Completion Coverage, Safe Rejection Rate, Unsafe Continuation Rate, semantic-unit replay, duplicate effects, missing units, payload bytes, technical failure rate, source-capture success rate.
