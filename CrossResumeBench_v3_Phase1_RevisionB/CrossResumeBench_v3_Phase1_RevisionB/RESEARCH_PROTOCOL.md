# Research Protocol — Phase 1 Revision B

## Hypothesis
For the frozen MCC v2 mechanism:

**H1:** With certified effect-commitment evidence, both hidden worlds complete safely across all six directed framework pairs.

**H2:** Without distinguishing effect-commitment evidence, the two hidden worlds produce byte-identical MCC payloads and are safely rejected.

**H3:** MCC v2 produces zero unsafe continuations.

## Two-world indistinguishability condition
For each source→target pair under `ambiguous_external_commit`:

```text
SHA256(MCC_payload_committed) == SHA256(MCC_payload_not_committed)
```

but the correct actions differ:

```text
committed      -> skip_effect
not_committed  -> execute_effect
```

This is the core impossibility-style experiment.

## Gate criteria
Full v3 may begin only if all of the following hold:

1. all three runtimes can technically restore a native checkpoint;
2. all six source captures succeed;
3. exactly 72 migration rows exist;
4. migration technical failures = 0;
5. all 12 MCC certified rows complete safely;
6. all 12 MCC ambiguous rows reject safely;
7. all six ambiguous world-pairs have identical MCC payload hashes;
8. certified committed/not-committed worlds make opposite correct decisions for all six pairs;
9. all 48 privileged controls complete safely.

Native self-resume **safety** is reported but is not a gate criterion. Native restore must be technically executable; a replay bug is a baseline result.

## Outcome taxonomy

### Safe completion
The target terminates with:

```json
{"effect_count":1,"ack_count":1,"finish_count":1}
```

and its effect decision matches hidden truth.

### Safe rejection
MCC refuses migration before target execution because the required effect fact cannot be established.

### Unsafe violation
MCC accepts and causes a wrong effect decision or ledger mismatch.

### Technical failure
The source checkpoint cannot be captured, the target runtime crashes, translation raises unexpectedly, or a runtime restore API cannot execute.

## Freeze discipline
Do not modify MCC v2 after observing Revision B results. If Revision B exposes a genuine MCC limitation, document it and create a separately named future mechanism version.
