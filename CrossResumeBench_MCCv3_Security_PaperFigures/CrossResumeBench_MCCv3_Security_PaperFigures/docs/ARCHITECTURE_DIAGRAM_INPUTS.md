# Inputs for the Next Architecture Diagram

The architecture diagram should be generated **after** the security result is reviewed. It should show, at minimum:

1. Source runtime checkpoint/capture (LangGraph / CrewAI / MAF).
2. Portable app state + history + attestations.
3. Target continuation contract.
4. Proof resolver:
   - identity canonicalization;
   - evidence verification;
   - history-derived facts;
   - complete snapshots;
   - conflict detection;
   - closed-world required-fact check.
5. Decision:
   - admissible → lower into target-native continuation;
   - unproven/invalid/conflicting → safe reject.
6. External-effect / obligation layer.
7. Trust boundary around attestation issuer.

Figure 1 in this package is a conceptual mechanism figure, not a substitute for the architecture diagram.
