from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class NativePause:
    framework: str
    case_id: str
    checkpoint_ref: str
    native_kind: str
    pending_work: list[str]
    app_state: dict[str, Any]
    history: list[dict[str, Any]]
    certificates: list[dict[str, Any]]
    native_observation: dict[str, Any]
    effect_count: int
    def to_dict(self): return asdict(self)

@dataclass
class RunOutcome:
    run_id: str
    source: str
    target: str
    case_id: str
    variant: str
    method: str
    safe_completion: int = 0
    safe_rejection: int = 0
    unsafe_violation: int = 0
    technical_failure: int = 0
    reject_reason: str | None = None
    failure_types: list[str] | None = None
    payload_bytes: int = 0
    artifact: dict[str, Any] | None = None
    def to_dict(self): return asdict(self)
