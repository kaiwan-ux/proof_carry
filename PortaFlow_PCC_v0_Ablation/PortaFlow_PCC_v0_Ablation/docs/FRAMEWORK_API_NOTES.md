# Framework API Notes Used by This Package

These notes document why the adapters/probes use the APIs they do. Re-check them if framework versions are changed.

## LangGraph

Official docs describe checkpoints at graph super-step boundaries and persistence via a checkpointer/thread ID. LangGraph interrupts resume by re-entering the interrupted node, so side effects before an interrupt must be idempotent or otherwise guarded.

- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/interrupts

## CrewAI

CrewAI Flows are event-driven workflows with shared Flow state. The current 1.15.17 docs describe `@start`, `@listen`, Flow state, persistence and resume behavior. This package uses class-level persistence for source evidence and a deterministic Flow entry point for target continuation.

- https://docs.crewai.com/en/concepts/flows

## Microsoft Agent Framework

MAF workflow checkpoints are produced at super-step boundaries and capture executor state, pending messages/requests and shared state. Python executors persist custom state through `on_checkpoint_save()` and restore it through `on_checkpoint_restore()`.

- https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints
- https://github.com/microsoft/agent-framework/blob/main/python/samples/03-workflows/checkpoint/checkpoint_with_resume.py

## Version discipline

This experiment intentionally pins the framework versions that were already exercised in the preceding successful native run. Changing versions is allowed only as an explicit compatibility patch, and the new versions must be recorded in the result environment files.
