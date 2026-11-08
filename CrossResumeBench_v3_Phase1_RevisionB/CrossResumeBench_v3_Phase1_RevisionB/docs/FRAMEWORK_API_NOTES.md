# Framework API Notes Used by Revision B

These notes document the API assumptions the experiment checks at runtime.

## CrewAI
Checkpointing is event-driven. `CheckpointConfig(on_events=["method_execution_finished"])` can be used for Flow checkpoints with `JsonProvider`. Revision B therefore leaves Flow events enabled and waits for a persisted checkpoint before stopping the source.

Reference checked during package design:
- CrewAI checkpointing documentation: https://crewai.ubitools.com/concepts/checkpointing/
- CrewAI repository/issues confirming `MethodExecutionFinishedEvent` and Flow checkpoint restoration paths: https://github.com/crewAIInc/crewAI

## Microsoft Agent Framework
`WorkflowContext[T_Out]` describes the type an executor sends downstream; `WorkflowContext[T_Out, T_WorkflowOut]` additionally describes yielded workflow output. Revision B uses primitive strings to avoid unsupported custom checkpoint serialization.

MAF checkpoints are created at superstep boundaries. Revision B uses `FileCheckpointStorage`, observes `superstep_completed`, lists checkpoints and resumes via `checkpoint_id`.

References checked during package design:
- https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints
- https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework.workflowcontext

## LangGraph
Revision B keeps the already-working Revision A LangGraph implementation: StateGraph + InMemorySaver + `interrupt_before=["ack"]`, followed by resume using the same thread configuration.
