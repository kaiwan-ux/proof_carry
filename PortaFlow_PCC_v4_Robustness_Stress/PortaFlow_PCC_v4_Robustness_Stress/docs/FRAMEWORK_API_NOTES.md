# Framework API notes (checked August 22, 2026)

The package retains the native wrapper strategy from the corrected Phase-0/PCC-v0 experiment.

- LangGraph: checkpointer-backed workflow execution and state snapshots.
- CrewAI: Flow execution and persistence/state capture.
- Microsoft Agent Framework: workflow checkpoint storage; executor checkpoint hooks use `on_checkpoint_save` / `on_checkpoint_restore`.

Official reference points checked while preparing this package:

- LangGraph persistence / interrupts: docs.langchain.com
- CrewAI Flows persistence: docs.crewai.com
- Microsoft Agent Framework checkpoints: learn.microsoft.com/en-us/agent-framework/workflows/checkpoints

The scientific representation is framework-neutral; exact APIs are experimental adapters and may evolve.
