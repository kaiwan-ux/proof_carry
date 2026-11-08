# Framework API Notes — verified 22 Aug 2026

These notes record the current official semantics used to design the native probes. They are not experimental results.

## LangGraph

Official persistence documentation states that graph state is checkpointed at super-step boundaries. Historical `StateSnapshot` objects expose values, next tasks, metadata and task/interrupt information. The interrupt documentation also states that resuming an `interrupt()` restarts the containing node from the beginning, so non-idempotent side effects before the interrupt may repeat.

References:
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/interrupts

## CrewAI Flows

CrewAI Flow `@persist` can save state after flow methods and uses SQLite persistence by default. Current documentation describes resume via the same state id and fork behavior via `restore_from_state_id`.

References:
- https://docs.crewai.com/
- https://github.com/crewAIInc/crewAI/blob/main/docs/v1.15.12/en/concepts/flows.mdx

## Microsoft Agent Framework

MAF graph workflows execute in super-steps. Checkpoints capture executor states, pending messages, pending requests/responses and shared state. Python currently supports in-memory/file checkpoint storage and resume by checkpoint id. The package may require prerelease installation.

References:
- https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints
- https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/
- https://learn.microsoft.com/en-us/agent-framework/get-started/

## Optional GPT-OSS-120B extension

Groq currently exposes model id `openai/gpt-oss-120b` through an OpenAI-compatible API base URL:

`https://api.groq.com/openai/v1`

References:
- https://console.groq.com/docs/model/openai/gpt-oss-120b
- https://console.groq.com/docs/openai
