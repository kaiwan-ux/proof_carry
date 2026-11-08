# Framework API Notes — Revision C

## Microsoft Agent Framework (the only adapter changed in Revision C)

Revision C follows the documented MAF workflow contract:

- Explicit handler types can be declared with `@handler(input=..., output=..., workflow_output=...)`; providing explicit types disables signature type introspection.
- `FileCheckpointStorage` provides durable local checkpoint storage.
- `superstep_completed` is used as the interruption point because the current superstep has completed and the checkpoint is durable.
- The latest checkpoint is obtained from storage and a fresh workflow instance resumes with `checkpoint_id` plus the same checkpoint storage.

Primary references used during design:

- https://github.com/microsoft/agent-framework/blob/main/python/samples/03-workflows/_start-here/step1_executors_and_edges.py
- https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints
- https://github.com/microsoft/agent-framework/blob/main/python/samples/03-workflows/checkpoint/checkpoint_with_resume.py

## CrewAI
Revision C retains the working Revision-B implementation unchanged: event-driven Flow checkpointing remains enabled, the source runs in a child process, and an external gate prevents ack from crossing the capture boundary before the checkpoint is persisted.

## LangGraph
Revision C retains the working Revision-B implementation unchanged: StateGraph + saver + native interrupt before `ack`, followed by native resume using the same thread configuration.
