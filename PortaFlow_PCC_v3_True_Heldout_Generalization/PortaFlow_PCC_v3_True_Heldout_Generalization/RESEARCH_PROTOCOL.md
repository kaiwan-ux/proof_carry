# Research Protocol — PCC v3 True Hold-out Generalization

## Frozen hypothesis

A continuation mechanism discovered on earlier workflows should generalize without retuning to new workflow structures.

### H1
`history + receipts` with generic semantic reconstruction will preserve all hard continuation invariants on the new hold-out suite.

### H2
`frontier + obligations + receipts + contract` will preserve the same invariants without history reconstruction.

### H3
History inference without receipts will remain conservative: it may reject ambiguous external-effect cases but should not perform unsafe continuation.

## Kill criteria

- If either frozen candidate needs workflow-specific patches after results are observed, its hold-out claim fails.
- If `history + receipts` develops unsafe violations, the hybrid-minimal claim is weakened.
- If `history_inference` completes the same cases as hybrid minimal with zero unsafe behavior, explicit receipts may not add value on this suite.
- If a much weaker control matches the frozen candidates, simplify/pivot.

## Claim boundary

This is empirical generalization over a pre-registered ten-workflow suite and current framework versions, not universal mathematical proof.
