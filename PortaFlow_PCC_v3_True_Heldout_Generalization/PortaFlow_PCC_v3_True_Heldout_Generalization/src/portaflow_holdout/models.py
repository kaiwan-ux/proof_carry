from __future__ import annotations
from dataclasses import dataclass, field, asdict
from copy import deepcopy
from typing import Any

@dataclass
class ExecutionState:
    workflow: str
    request_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    retry_counts: dict[str, int] = field(default_factory=dict)
    decisions: dict[str, str] = field(default_factory=dict)
    loop_counters: dict[str, int] = field(default_factory=dict)
    control_frontier: dict[str, Any] = field(default_factory=dict)
    pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    effect_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    continuation_contract: dict[str, Any] = field(default_factory=dict)
    terminated: bool = False
    outcome: str | None = None

    def clone(self) -> "ExecutionState":
        return ExecutionState.from_dict(self.to_dict())

    def event(self, kind: str, step: str, **detail: Any) -> None:
        self.trace.append({"seq": len(self.trace)+1, "kind": kind, "step": step, "detail": deepcopy(detail)})

    def step(self, step: str) -> None:
        self.completed.append(step)
        self.event("step_completed", step)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ExecutionState":
        return cls(
            workflow=d["workflow"], request_id=d["request_id"], inputs=deepcopy(d.get("inputs", {})),
            trace=deepcopy(d.get("trace", [])), completed=list(d.get("completed", [])),
            retry_counts=deepcopy(d.get("retry_counts", {})), decisions=deepcopy(d.get("decisions", {})),
            loop_counters=deepcopy(d.get("loop_counters", {})), control_frontier=deepcopy(d.get("control_frontier", {})),
            pending_obligations=deepcopy(d.get("pending_obligations", [])), effect_receipts=deepcopy(d.get("effect_receipts", {})),
            continuation_contract=deepcopy(d.get("continuation_contract", {})), terminated=bool(d.get("terminated", False)),
            outcome=d.get("outcome"),
        )

@dataclass
class SourceCapture:
    framework: str
    workflow: str
    state: dict[str, Any]
    native_snapshot: dict[str, Any]
    external_ledger: dict[str, int]
    def to_dict(self): return asdict(self)

@dataclass
class RunRecord:
    run_id: str
    source_framework: str
    target_framework: str
    workflow: str
    condition: str
    safe_completion: int
    migration_rejected: int
    unsafe_violation: int
    technical_failure: int
    failure_types: str
    ambiguity_count: int
    inferred_fields: int
    capsule_bytes: int
    duplicate_effects: int
    replayed_steps: int
    wrong_outcome: int
    wrong_ledger: int
    wrong_trace: int
    source_snapshot_kind: str
    notes: str = ""
    def to_dict(self): return asdict(self)
