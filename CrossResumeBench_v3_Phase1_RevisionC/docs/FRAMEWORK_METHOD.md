# Framework Method — Revision C

## LangGraph — unchanged from Revision B
The source graph executes `effect_attempt`, then pauses with a native interrupt before `ack` using the graph saver. The checkpoint has `ack` pending. Native self-resume continues from the same thread configuration.

## CrewAI — unchanged from Revision B
CrewAI Flow checkpointing is configured on `method_execution_finished` with `JsonProvider`.

The source Flow runs in a child process. After `effect_attempt` returns, the downstream `ack` stage is held behind an external gate. The parent process waits until a real checkpoint file exists, verifies that the ledger still has `ack_count=0`, and only then stops the source process. Native restore uses CrewAI's checkpoint restore path.

## Microsoft Agent Framework — corrected in Revision C
Revision C deliberately avoids runtime inspection of locally scoped `WorkflowContext[...]` annotations.

Forwarding executors declare their message contract explicitly:

```python
@handler(input=str, output=str)
```

The terminal executor declares:

```python
@handler(input=str, workflow_output=str)
```

This uses MAF's all-explicit handler mode.

The source workflow is built with `FileCheckpointStorage`. Execution stops only after the `effect_attempt` superstep emits `superstep_completed`, which is treated as the durable checkpoint boundary. The adapter then calls:

```text
storage.get_latest(workflow_name=workflow.name)
```

and verifies that neither `ack` nor `finish` has executed.

Native self-resume rebuilds the same workflow wiring and resumes with the captured `checkpoint_id` and checkpoint storage. MAF target tests use the same explicit handler declarations and verify both decisions:

```text
committed      -> skip_effect -> ack -> finish
not_committed  -> execute_effect -> ack -> finish
```
