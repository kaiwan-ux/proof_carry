from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import copy, json

@dataclass
class ActionSpec:
    action_id: str
    semantic_unit: str
    kind: str = "step"  # step|effect|approval|callback|join|compensation|finish
    operation: str | None = None
    depends_on: list[str] = field(default_factory=list)
    parent_unit: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d): return cls(**copy.deepcopy(d))

@dataclass
class SemanticCertificate:
    certificate_id: str
    fact_type: str  # effect_commitment|semantic_completion|obligation_state|dependency_state
    subject: str
    value: Any
    scope: str
    evidence: dict[str, Any]
    issuer: str = "crossresumebench_witness"
    evidence_hash: str = ""
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d): return cls(**copy.deepcopy(d))

@dataclass
class SourceCapture:
    case_id: str
    workflow: str
    app_state: dict[str, Any]
    portable_history: list[dict[str, Any]]
    certificates: list[dict[str, Any]]
    source_ledger: dict[str, int]
    native_observation: dict[str, Any] = field(default_factory=dict)
    # Ground truth is evaluator-only and MUST NOT enter MCC transfer.
    truth_completed_units: list[str] = field(default_factory=list)
    truth_pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    truth_dependencies: dict[str, list[str]] = field(default_factory=dict)
    truth_decisions: dict[str, str] = field(default_factory=dict)
    truth_counters: dict[str, int] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class ReconstructedContinuation:
    case_id: str
    workflow: str
    app_state: dict[str, Any]
    completed_units: list[str] = field(default_factory=list)
    pending_obligations: list[dict[str, Any]] = field(default_factory=list)
    effect_facts: dict[str, dict[str, Any]] = field(default_factory=dict)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    decisions: dict[str, str] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)
    ambiguities: list[dict[str, Any]] = field(default_factory=list)
    inference_log: list[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d): return cls(**copy.deepcopy(d))

@dataclass
class CaseSpec:
    case_id: str
    family: str
    variant: int
    app_state: dict[str, Any]
    source_actions: list[dict[str, Any]]
    target_actions: list[dict[str, Any]]
    target_dependencies: dict[str, list[str]]
    expected_semantic_units: list[str]
    expected_effect_counts: dict[str, int]
    mismatch_tags: list[str]
    source_boundary: str
    target_boundary: str
    metadata: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d): return cls(**copy.deepcopy(d))

@dataclass
class TransferPackage:
    name: str
    payload: dict[str, Any]
    accepted: bool = True
    reject_reason: str | None = None
    inference_report: dict[str, Any] = field(default_factory=dict)
    def byte_size(self):
        return len(json.dumps(self.payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())

@dataclass
class TargetResult:
    completed_units: list[str]
    executed_units: list[str]
    final_ledger: dict[str, int]
    outcome: str | None
    terminated: bool
    native_artifact: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class EvalResult:
    safe_completion: int
    safe_rejection: int
    unsafe_violation: int
    failure_types: list[str]
    duplicate_effects: int = 0
    replayed_units: int = 0
    missing_units: int = 0
    wrong_ledger: int = 0
    wrong_outcome: int = 0
    def to_dict(self): return asdict(self)
