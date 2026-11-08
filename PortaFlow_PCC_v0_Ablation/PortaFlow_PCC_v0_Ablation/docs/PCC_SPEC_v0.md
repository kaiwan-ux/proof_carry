# Portable Continuation Capsule — PCC v0

PCC v0 is a framework-independent representation of the **remaining logical obligations** of an in-progress agent workflow.

## Section 1 — Application state

Examples: request ID, amount, retry limit. These are ordinary domain variables and are insufficient on their own.

## Section 2 — Semantic history

Portable observations of completed logical actions. History is intentionally not treated as proof that an external effect committed or that a pending request handle remains valid.

## Section 3 — Control frontier

Defines where legal continuation begins, including branch/loop progress.

Examples:

```json
{"next":"left_action","branch_choice":"left"}
```

```json
{"next":"loop_body_3","iteration":3,"limit":3}
```

## Section 4 — Pending obligations

Represents unresolved work that must survive migration, such as:

- human approval request
- retry obligation
- pending parallel branch

## Section 5 — Effect receipts

Represents externally committed effects and replay policy:

```json
{
  "operation_id":"pcc-side_effect-001",
  "status":"committed",
  "replay":"forbidden",
  "idempotency_key":"idem-pcc-side_effect-001"
}
```

This section exists because ordinary history cannot safely distinguish “tool observed” from “external effect durably committed.”

## Section 6 — Continuation/dependency contract

Defines hard execution obligations that cannot always be reconstructed from a sequence of events alone. PCC v0 currently uses this for parallel join/exactly-once semantics.

## Explicit non-goals

PCC v0 does not serialize:

- Python call stacks
- runtime threads
- framework-private checkpoint blobs
- model hidden state
- arbitrary in-flight network connections

The research target is **logical continuation semantics**, not machine-process migration.
