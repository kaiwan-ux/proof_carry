# Related-work baseline notes

## AAIF
AAIF v3 defines an `agent-state` checkpoint with pipeline position, conversation, pending tool calls, memory and a cross-platform migration protocol. This project includes only a **reference projection** of those concepts (`aaif_state_strict`) plus a combined reference condition with durable receipts. Before publication, integrate/validate against the official AAIF schema/toolchain and describe exact deviations.

## CapLease
CapLease studies durable authorization consumption and Issue–Prepare–Commit state for replay-resistant agent actions. `caplease_inspired` here models only the high-level durable effect-evidence role; it is **not** the authors' implementation. Before a direct comparison, use their released artifact if available and follow their evaluation assumptions.
