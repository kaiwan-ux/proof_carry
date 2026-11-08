# Framework Method — Revision B

## LangGraph
The source graph executes `effect_attempt`, then pauses with `interrupt_before=["ack"]` using `InMemorySaver`. The checkpoint has `ack` pending. Native self-resume continues from the same thread configuration.

## CrewAI
CrewAI Flow checkpointing is configured on `method_execution_finished` with `JsonProvider`.

Revision B explicitly **does not suppress Flow events**. The source Flow runs in a child process. After `effect_attempt` returns, the downstream `ack` listener waits on an external file gate. The parent process waits until a real checkpoint file exists, verifies the ledger still has `ack_count=0`, and then stops the child. This avoids the Revision A race where an exception could occur before event-driven checkpoint persistence.

Native self-resume uses the framework's checkpoint restore path. If restore technically completes but replays the committed effect, that is recorded as a native-baseline safety failure rather than an adapter error.

## Microsoft Agent Framework
Revision B uses `FileCheckpointStorage` and primitive string messages. Executors use:

- `WorkflowContext[str]` when sending a string downstream;
- `WorkflowContext[Never, str]` for the terminal executor yielding a string output.

The source stream stops after a real `superstep_completed` event following the effect executor. The latest persisted checkpoint is selected. Native self-resume rebuilds an equivalent workflow with stable name/executor IDs and calls `workflow.run(checkpoint_id=..., checkpoint_storage=...)`.
