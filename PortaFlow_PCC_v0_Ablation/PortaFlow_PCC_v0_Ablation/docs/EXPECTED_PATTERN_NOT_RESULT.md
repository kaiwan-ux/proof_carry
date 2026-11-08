# Expected Pattern — NOT Research Evidence

The unit tests use a deterministic fake adapter to verify that the *experiment machinery* can detect the intended ablation categories. In that self-test only, the designed safe-case counts are:

- state_only: 0/36
- state_history: 6/36
- plus_control_frontier: 18/36
- plus_pending_obligations: 24/36
- plus_effect_receipts: 30/36
- full_pcc_v0: 36/36

These are **test expectations**, not native framework findings and must never be pasted into the proposal as experimental results.

The delivered `results/` directory starts clean. Only the user's run of the native framework package produces evidence.
