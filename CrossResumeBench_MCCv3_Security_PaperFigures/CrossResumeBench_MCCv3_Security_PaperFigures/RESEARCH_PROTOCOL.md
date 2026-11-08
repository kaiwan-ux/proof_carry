# Research Protocol

## Frozen evidence
The passed MCC v3 holdout and post-validation outputs are read-only inputs. Their hashes are verified before any new analysis.

## New study
The security study has 16 new proof-layer scenarios (2 per semantic family), 6 directed runtime labels, and 8 attack/control variants = **768 rows**.

### In-threat-model integrity cases
- valid control
- value tamper without rehash
- subject tamper without rehash
- evidence tamper without rehash
- continuation-contract hash tamper
- conflicting valid certificates

### Explicit trust-boundary cases
- cross-context replay of a still-valid certificate
- forged wrong value with recomputed hash

The final two are intentionally outside MCC v3's current trusted-witness threat model. They are included to define, not hide, the security boundary.

## Primary security gate
PASS requires:
- valid controls complete safely;
- all in-threat-model mutations/conflicts reject safely;
- zero technical failures.

Out-of-model replay/forgery is reported separately and must **not** be used to claim cryptographic security.

## Visualization protocol
All paper figures are regenerated only from frozen result files or from the new security CSV. Each figure exports PDF, SVG, PNG (600 DPI), plus source-data CSV.
