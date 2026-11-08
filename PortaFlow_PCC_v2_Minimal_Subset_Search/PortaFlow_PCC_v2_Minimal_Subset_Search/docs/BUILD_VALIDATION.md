# Build Validation (software QA only — not research evidence)

Before delivery, the package was validated with deterministic/fake adapters solely to test the experiment machinery.

- Python compilation: PASS
- Unit/research tests: 8/8 PASS
- Exhaustive search shape: 1,024 workflow rows / 128 subset summaries PASS
- Automatic minimal-candidate selection: PASS
- Native-confirmation matrix shape with fake adapters: 384 rows PASS
- Unique run IDs: PASS
- Safe-rejection path: PASS
- Anti-native-checkpoint leakage scan: PASS
- Analysis + graph pipeline: PASS
- Result verifier: `ok: true`
- Manifest/export pipeline: PASS

All validation outputs were deleted before packaging. The shipped `results/` directory is clean and must not be treated as containing experiment evidence.
