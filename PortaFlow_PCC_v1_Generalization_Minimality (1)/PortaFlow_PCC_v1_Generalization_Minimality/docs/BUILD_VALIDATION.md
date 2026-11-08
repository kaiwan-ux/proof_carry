# Build validation

Before delivery, the package was validated with deterministic fake adapters (not research evidence):

- Python compilation: PASS
- Unit/research tests: 7/7 PASS
- Hold-out workflow-name separation: PASS
- Non-redacted history test: PASS
- ambiguity-safe-rejection test: PASS
- anti-native-checkpoint leakage test: PASS
- full PCC logical completion test across all 8 hold-outs: PASS
- full configured 432-row matrix generation: PASS
- unique run IDs: PASS
- analysis pipeline: PASS
- result verifier: PASS
- manifest/checksum pipeline: PASS

All fake-adapter validation outputs are removed before packaging. The delivered `results/` directory starts clean.
