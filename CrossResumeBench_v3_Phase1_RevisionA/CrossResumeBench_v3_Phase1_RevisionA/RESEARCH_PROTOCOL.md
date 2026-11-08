# Research Protocol — Revision A

## Frozen mechanism
MCC v2 is an unchanged experimental subject. Do not patch it after observing Revision-A results.

## Primary falsification
Two hidden worlds have identical transferable ambiguous evidence but require opposite continuation decisions. A history-only/uncertified continuation cannot safely choose one action for both worlds. The expected MCC v2 outcome is conservative rejection.

## Gate requirements
All must pass:

1. All three native self-resume controls succeed.
2. All six source captures succeed (3 runtimes × 2 worlds).
3. Exactly 72 migration rows are present and unique.
4. Zero migration technical failures.
5. MCC v2 certified cases: 12/12 safe completions, 0 unsafe.
6. MCC v2 ambiguous cases: 12/12 safe rejections, 0 completion, 0 unsafe.
7. Ambiguous committed/not-committed MCC payload hashes are identical for every directed pair.
8. Oracle and explicit-minimal controls complete 48/48 safely.

A gate failure is data. Fix only infrastructure/test invalidity. If the corrected benchmark exposes a frozen MCC v2 limitation, document it; do not silently patch v2.
