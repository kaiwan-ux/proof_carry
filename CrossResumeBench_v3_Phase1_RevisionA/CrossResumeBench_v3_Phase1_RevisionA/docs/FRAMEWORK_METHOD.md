# Framework Method

## LangGraph
Source graph runs `effect_attempt`, then uses `interrupt_before=["ack"]`. The checkpoint has `ack` pending. Self-resume continues from the same thread/checkpoint.

## CrewAI
Flow checkpointing is configured on `method_execution_finished`. `effect_attempt` finishes and is checkpointed. The downstream `ack` method raises a controlled Phase-1 stop before any acknowledgment side effect. Self-resume uses `Flow.from_checkpoint(CheckpointConfig(restore_from=...))` with a resume gate.

## Microsoft Agent Framework
A workflow checkpoint is created after supersteps. The source stream is stopped at the `superstep_completed` event after `effect_attempt`, then the latest native checkpoint is used for self-resume. All async work stays within one event loop per public operation.
