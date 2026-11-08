# Framework API Notes

The package intentionally uses the checkpoint patterns already proven in Revision C:
- LangGraph: checkpointer + interrupt-before-resume boundary.
- CrewAI: event-driven `method_execution_finished` checkpoint, source process held in a downstream external gate, restored via `Flow.from_checkpoint`.
- Microsoft Agent Framework: `FileCheckpointStorage`, explicit handler type declarations, stop at `superstep_completed`, resume by `checkpoint_id`.

The full benchmark generalizes these durable native boundaries to seven deterministic semantic micro-workflows. It does not pretend that every family is implemented with each framework's highest-level convenience primitive.
