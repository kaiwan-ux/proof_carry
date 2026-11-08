from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import copy, json

@dataclass
class Event:
    seq: int
    type: str
    step: str
    data: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class EffectReceipt:
    operation_id: str
    status: str
    replay: str = "forbidden"
    idempotency_key: str | None = None
    source: str = "certified_sink"
    def to_dict(self): return asdict(self)

@dataclass
class RuntimeState:
    case_id: str
    workflow: str
    app_state: dict[str, Any] = field(default_factory=dict)
    completed_steps: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    frontier: dict[str, Any] = field(default_factory=dict)
    pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    effect_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    contract: dict[str, Any] = field(default_factory=dict)
    retry_counts: dict[str, int] = field(default_factory=dict)
    decisions: dict[str, str] = field(default_factory=dict)
    loop_counters: dict[str, int] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)
    outcome: str | None = None
    terminated: bool = False
    def clone(self): return copy.deepcopy(self)
    def event(self, typ:str, step:str, **data):
        self.history.append(Event(len(self.history)+1,typ,step,data).to_dict())
    def step(self, step:str):
        if step not in self.completed_steps: self.completed_steps.append(step)
        self.trace.append(step)
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d): return cls(**copy.deepcopy(d))

@dataclass
class CaseSpec:
    case_id: str
    family: str
    variant: int
    static_graph: dict[str, Any]
    source_state: dict[str, Any]
    source_ledger: dict[str, int]
    reference_final_state: dict[str, Any]
    reference_final_ledger: dict[str, int]
    mismatch_tags: list[str]
    source_boundary: str
    target_boundary: str
    metadata: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class TransferPackage:
    name: str
    payload: dict[str, Any]
    inference_report: dict[str, Any] = field(default_factory=dict)
    accepted: bool = True
    reject_reason: str | None = None
    def byte_size(self):
        return len(json.dumps(self.payload,sort_keys=True,separators=(",",":")).encode())

@dataclass
class EvalResult:
    safe_completion: int
    safe_rejection: int
    unsafe_violation: int
    failure_types: list[str]
    duplicate_effects: int = 0
    replayed_steps: int = 0
    wrong_ledger: int = 0
    wrong_outcome: int = 0
    def to_dict(self): return asdict(self)
