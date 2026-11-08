# Native Runtime API Notes

This package deliberately pins framework versions because native persistence APIs are version-sensitive.

## LangGraph

The adapter uses `StateGraph` with `InMemorySaver`, pauses before the continuation node, verifies the checkpoint's next node, and resumes using the same thread configuration. Target continuation is executed through a LangGraph target graph.

## CrewAI

The adapter uses actual Flow checkpointing with `CheckpointConfig` and `JsonProvider`. The source workflow pauses behind an external gate only after its source-boundary method has completed. The adapter requires a persisted checkpoint file. It tries `method_execution_finished` first and, if necessary, an `on_events=["*"]` checkpoint profile. Resume is version-compatible: `Flow.from_checkpoint(CheckpointConfig(...))` when present, otherwise `kickoff(from_checkpoint=CheckpointConfig(...))` when supported.

No synthetic fallback is permitted. Failure to observe a real checkpoint is a technical failure.

## Microsoft Agent Framework

The adapter uses `FileCheckpointStorage`, explicit typed handlers, a real workflow checkpoint, and checkpoint-ID rehydration. Target continuation executes through a target MAF workflow.

## Important interpretation

A successful native family gate demonstrates the persistence/resume path used by this benchmark on that installed framework version. It does not prove equivalence of arbitrary framework internals or all production workloads.
