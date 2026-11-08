# Build Validation

Validated before packaging:

- immutable input hash verification: PASS (15 files)
- frozen MCC v3 mechanism present: PASS
- security suite: 16 cases × 6 directed runtime labels × 8 variants = 768 rows
- security valid controls: 96/96 safe completion
- in-threat-model mutations/conflicts: 480/480 safe rejection
- in-threat-model unsafe: 0
- explicit trust-boundary attacks: 192/192 unsafe, as expected under the documented out-of-model attacker assumptions
- publication figures: 11 PNG + 11 PDF + 11 SVG
- figure source-data CSVs: generated
- tests: 3/3 PASS
- output verifier: PASS

The 192 trust-boundary rows are not failures of the sealed MCC v3 holdout claim. They demonstrate that a plain integrity hash is not issuer authentication or replay protection.
