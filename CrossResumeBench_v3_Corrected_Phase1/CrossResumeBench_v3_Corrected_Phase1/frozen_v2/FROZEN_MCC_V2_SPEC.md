# Frozen MCC v2 Specification

## Core rule
MCC v2 transfers **evidence, not reconstructed target state**. The target reconstructs continuation semantics.

The transfer contains only: application state, portable semantic history, and typed semantic certificates. A certificate can assert an external-effect commitment, semantic-unit completion, pending obligation state, or dependency state. It carries an evidence hash and scope. It is **not** a source-native checkpoint blob.

### Safety rule
1. Infer facts that are uniquely supported by portable history + public target workflow structure.
2. Apply valid certificates to facts that are not safely inferable.
3. If a required external commitment or semantic-completion fact remains ambiguous, **reject migration**.

### Critical distinction learned from v1
`external effect committed` does **not** imply `enclosing semantic workflow unit completed` unless that implication is explicit in workflow semantics or separately certified.

### Anti-leak rule
MCC v2 must never contain `state`, `frontier`, `completed_steps`, `completed_units`, `native_checkpoint`, `checkpoint_id`, `flow_id`, `thread_id`, `source_native_snapshot`, or executor-state blobs. JSON Schema validation enforces the transport shape and a recursive forbidden-key scan provides a second check.
