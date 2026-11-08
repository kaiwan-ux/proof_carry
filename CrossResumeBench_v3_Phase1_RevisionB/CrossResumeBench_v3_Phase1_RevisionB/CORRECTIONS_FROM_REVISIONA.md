# Corrections from Phase 1 Revision A

Revision B changes **benchmark infrastructure only**. MCC v2, the two-world semantics and the evidence variants are frozen.

## 1. CrewAI checkpoint race / event suppression
Revision A combined `CheckpointConfig(on_events=["method_execution_finished"])` with `suppress_flow_events=True` and an exception-based pause in the next listener. That design could suppress or race the very event used to persist the checkpoint.

Revision B removes event suppression and exception-first pausing. The Flow executes in a child process; the post-effect listener blocks on a file gate while the parent waits for the checkpoint file. Only after the checkpoint exists does the parent stop the source process.

## 2. CrewAI native restore is a control, not an assumption
Revision B no longer requires native self-resume to be safe in order for the cross-runtime experiment to be scientifically interpretable. If restore completes but duplicates a committed effect, the row is `native_unsafe_replay=1`, not `technical_failure=1`.

## 3. MAF handler types
Revision A used `WorkflowContext[dict]`. Revision B avoids ambiguous generic dictionary typing and uses JSON strings with `WorkflowContext[str]`; terminal output uses `WorkflowContext[Never, str]`.

## 4. MAF durable checkpoints
Revision B uses `FileCheckpointStorage`, stops at a real `superstep_completed` event, lists persisted checkpoints, and resumes a newly built workflow from the selected `checkpoint_id`.

## 5. Analysis truthfulness
Generated summaries are calculated directly from CSV rows. Revision B contains tests that verify pair summaries and certified-world decisions against raw results.

## 6. Structural verification
The verifier enforces exactly 72 migration rows, 24 rows per method, 12 rows per directed pair, unique run IDs, and exactly one terminal outcome per row.
