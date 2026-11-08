# Build Validation

- Expanded case audit: PASS (120 total, 8 families, 15 each, no duplicate IDs/scenario kinds/titles/descriptions).
- Legacy sealed evidence audit: PASS (6,144 migration rows, 32 base cases, 8 methods).
- Unit tests: PASS (6/6).
- Full deterministic semantic/security/ablation/runtime-identity run: PASS.
- Full performance harness: 21,600 measured rows (120 cases x 6 pairs x 30 repetitions).
- Expanded native validation: NOT RUN in the build environment; no native success is fabricated.

Final release reference run: `proofcarry-20260829T201030Z-93eb8fd9`.
