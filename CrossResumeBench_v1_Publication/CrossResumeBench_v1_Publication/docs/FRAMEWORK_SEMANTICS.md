# Framework semantic notes (checked August 2026)
- LangGraph checkpoints graph state at super-step boundaries; dynamic `interrupt()` resumes by re-entering the node, so pre-interrupt side effects must be idempotent or otherwise protected.
- CrewAI 1.15.17 exposes first-class checkpointing for Crew, Flow and Agent, with event-triggered checkpoints and resume/fork behavior; completed tasks are skipped on restore.
- Microsoft Agent Framework checkpoints executor state, pending messages/requests and shared state at super-step boundaries and can rehydrate compatible workflows.

The focused probes in `native_probes/` record concrete runtime behavior. Keep their raw stdout/stderr in the result artifact.
