# Corrected v3 Design Specification

## Frozen mechanism
MCC v2 is unchanged. The research mechanism is the exact v2 implementation under `frozen_v2/`.

## Phase-1 experiment
### Common semantic state
An irreversible external operation has committed. The source runtime has not yet executed the logical acknowledgment step.

### Why this case first
All three runtimes can represent a durable boundary after one unit of work and before the next. It directly tests the distinction central to MCC: an external effect may already be committed even though execution is still in flight.

### Native source semantics
- **LangGraph**: checkpoint after `commit_effect`, static pause before `ack`.
- **CrewAI**: Flow checkpoint after `commit_effect` method; restore from that native checkpoint.
- **MAF**: workflow checkpoint after the `commit_effect` executor superstep, before `ack` executor.

### Cross-runtime migration
The source checkpoint itself is never loaded by another framework. Source-native state is converted to schema-valid MCC evidence. The target reconstructs continuation and executes its own native `ack -> finish` flow.

### Outcomes
- Safe completion: final ledger count remains exactly 1; `ack` and `finish` execute once.
- Safe rejection: target never starts because the effect commit is ambiguous.
- Unsafe: effect replay, missing acknowledgment, wrong outcome, or hidden native state leakage.

## Capability matrix before full v3
For each planned pause point record:
- support classification;
- native checkpoint artifact type;
- exact resume API;
- same-runtime self-resume result;
- whether pending work is visible in checkpoint metadata.

Only validated pause points enter the full benchmark.

## Full-v3 rule
The later benchmark uses an evidence-applicability matrix, not `all cases × all variants`. The base workflow case is the primary statistical unit; framework directions are paired repeated observations, not independent samples.
