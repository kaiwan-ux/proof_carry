
# CrewAI Repair Notes

The repaired adapter is copied from the successful Phase-1 Revision-C CrewAI implementation.

The earlier failure mode was `CrewAI produced no method_execution_finished checkpoint before controlled stop`. The repair avoids the checkpoint race by leaving Flow events enabled and moving the source flow into a subprocess. `effect_attempt` completes, a signal file is written, and the next listener waits on an external gate. The parent polls the durable checkpoint directory and stops the child only after a checkpoint exists and the ledger confirms ACK/finish have not run.

This file documents adapter engineering only; it does not modify the research mechanism.
