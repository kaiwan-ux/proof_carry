# Frozen MCC v1 specification
MCC transfers only:
1. portable semantic event history;
2. certified effect receipts for externally committed operations.

At the target, a deterministic reconstruction pass uses the public workflow structure to infer completed semantic work, decisions, loop/retry progress, pending obligations, and control/dependency information. A migration is admissible only if every critical fact needed to choose between mutually incompatible continuation actions is established either by reconstruction or by a certificate. Otherwise MCC rejects migration.

MCC does not carry a source-native LangGraph/CrewAI/MAF checkpoint blob.
