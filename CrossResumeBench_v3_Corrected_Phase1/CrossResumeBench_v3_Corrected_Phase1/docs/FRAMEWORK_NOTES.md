# Framework Notes

## LangGraph
Use a checkpointer and a stable `thread_id`. The common Phase-1 pause is a static `interrupt_before=["ack"]` boundary after the effect node. This avoids pretending that arbitrary Python lines are resumable.

## CrewAI
Use deterministic `Flow`, `CheckpointConfig`, and a checkpoint emitted after `method_execution_finished`. Restore with `Flow.from_checkpoint(...)`. CrewAI checkpoint support is version-sensitive; the capability probe must record the API actually present.

## Microsoft Agent Framework (MAF)
Use `agent_framework`, `WorkflowBuilder`, and `InMemoryCheckpointStorage`. MAF checkpoints are superstep-boundary artifacts containing executor state and pending workflow messages/requests. This package never imports AutoGen for the MAF path.
