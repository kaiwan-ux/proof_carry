from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class LogicalState:
    workflow: str
    request_id: str
    amount: int = 100
    max_retries: int = 2
    completed: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    retry_attempts: int = 0
    pending_approval: bool = False
    approval_request_id: str | None = None
    approved: bool | None = None
    effect_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    control_frontier: dict[str, Any] = field(default_factory=dict)
    pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    branch_choice: str | None = None
    loop_iteration: int = 0
    parallel_completed: list[str] = field(default_factory=list)
    dependency_contract: dict[str, Any] = field(default_factory=dict)
    terminated: bool = False
    outcome: str | None = None

    def event(self, kind: str, step: str, **detail: Any) -> None:
        self.trace.append({"seq": len(self.trace)+1, "kind": kind, "step": step, "detail": detail})

    def step(self, name: str) -> None:
        self.event("step_completed", name)
        self.completed.append(name)

    def clone(self) -> "LogicalState":
        return LogicalState.from_dict(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LogicalState":
        return cls(
            workflow=d["workflow"], request_id=d["request_id"], amount=int(d.get("amount", 100)),
            max_retries=int(d.get("max_retries", 2)), completed=list(d.get("completed", [])),
            trace=[dict(x) for x in d.get("trace", [])], retry_attempts=int(d.get("retry_attempts", 0)),
            pending_approval=bool(d.get("pending_approval", False)), approval_request_id=d.get("approval_request_id"),
            approved=d.get("approved"), effect_receipts=dict(d.get("effect_receipts", {})),
            control_frontier=dict(d.get("control_frontier", {})),
            pending_obligations=[dict(x) for x in d.get("pending_obligations", [])],
            branch_choice=d.get("branch_choice"), loop_iteration=int(d.get("loop_iteration", 0)),
            parallel_completed=list(d.get("parallel_completed", [])),
            dependency_contract=dict(d.get("dependency_contract", {})),
            terminated=bool(d.get("terminated", False)), outcome=d.get("outcome"),
        )

@dataclass
class SourceCapture:
    framework: str
    workflow: str
    state: dict[str, Any]
    native_snapshot: dict[str, Any]
    external_ledger: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class RunRecord:
    run_id: str
    source_framework: str
    target_framework: str
    workflow: str
    condition: str
    safe_continuation: int
    technical_failure: int
    failure_types: str
    duplicate_effects: int
    replayed_steps: int
    approval_preserved: int
    retry_preserved: int
    branch_preserved: int
    loop_preserved: int
    parallel_preserved: int
    correct_termination: int
    source_native_kind: str
    pcc_bytes: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
