# Research Protocol — Phase 1 Revision C

## Change-control rule
Revision C changes **only Microsoft Agent Framework adapter engineering** relative to Revision B. MCC v2, LangGraph, CrewAI, the two-world semantics, evidence construction, migration methods, safety oracle and result matrix remain frozen.

## Hypotheses

**H1:** With certified effect-commitment evidence, both hidden worlds complete safely across all six directed framework pairs.

**H2:** Without distinguishing effect-commitment evidence, the two hidden worlds produce byte-identical MCC payloads and are safely rejected.

**H3:** Frozen MCC v2 produces zero unsafe continuations.

## Two-world indistinguishability condition
For each source→target pair under `ambiguous_external_commit`:

```text
SHA256(MCC_payload_committed) == SHA256(MCC_payload_not_committed)
```

while the correct actions differ:

```text
committed      -> skip_effect
not_committed  -> execute_effect
```

## Revision-C MAF pre-gate
The full benchmark must not start until `scripts/probe_maf_revisionC.py` proves that MAF can:

1. build handlers using explicit decorator types;
2. capture a real checkpoint after the effect-attempt superstep;
3. stop before ack/finish;
4. restore the committed checkpoint;
5. act as a target for both `committed` and `not_committed` decisions.

A failure here is classified as MAF adapter/framework integration evidence, not an MCC failure.

## Full gate criteria
Full v3 may begin only if all hold:

1. the Revision-C MAF pre-gate passes;
2. all three runtimes can technically restore a native checkpoint;
3. all six source captures succeed;
4. exactly 72 migration rows exist;
5. migration technical failures = 0;
6. all 12 MCC certified rows complete safely;
7. all 12 MCC ambiguous rows reject safely;
8. all six ambiguous world-pairs have identical MCC payload hashes;
9. certified committed/not-committed worlds make opposite correct decisions for all six pairs;
10. all 48 privileged controls complete safely.

Native self-resume **safety** is reported separately and is not itself a gate criterion. Technical restore capability is required.

## Freeze discipline
Do not modify MCC v2 after observing Revision C. A genuine MCC limitation must be documented and, if needed, addressed only in a separately named future mechanism version.
