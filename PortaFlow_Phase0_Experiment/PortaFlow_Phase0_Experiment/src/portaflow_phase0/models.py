from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Event:
    seq: int
    kind: str
    step: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeState:
    workflow: str
    variant: int
    vars: dict[str, Any] = field(default_factory=dict)
    current_step: str = "start"
    completed: list[str] = field(default_factory=list)
    trace: list[Event] = field(default_factory=list)
    effects: dict[str, int] = field(default_factory=dict)
    branch_choice: str | None = None
    loop_iteration: int = 0
    retry_attempts: int = 0
    pending_approval: bool = False
    approved: bool | None = None
    terminated: bool = False
    outcome: str | None = None

    def emit(self, kind: str, step: str, **detail: Any) -> None:
        self.trace.append(Event(len(self.trace), kind, step, detail))

    def complete(self, step: str) -> None:
        self.completed.append(step)
        self.current_step = step
        self.emit("step_completed", step)

    def effect(self, name: str) -> None:
        self.effects[name] = self.effects.get(name, 0) + 1
        self.emit("effect_committed", name, count=self.effects[name])

    def clone(self) -> "RuntimeState":
        data = self.to_dict()
        data["trace"] = [Event(**e) for e in data["trace"]]
        return RuntimeState(**data)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["trace"] = [e.to_dict() for e in self.trace]
        return d


@dataclass
class Capsule:
    condition: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"condition": self.condition, "payload": self.payload}


@dataclass
class Evaluation:
    safe: bool
    invariant_results: dict[str, bool]
    failure_types: list[str]
    notes: list[str] = field(default_factory=list)


@dataclass
class RunRecord:
    run_id: str
    evidence_tier: str
    source_framework: str
    target_framework: str
    workflow: str
    condition: str
    variant: int
    safe_continuation: int
    technical_failure: int
    failure_types: str
    invariant_results: str
    source_boundary: str
    final_outcome: str
    duplicate_effects: int
    replayed_steps: int
    skipped_required_steps: int
    approval_preserved: int
    retry_preserved: int
    correct_termination: int
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
