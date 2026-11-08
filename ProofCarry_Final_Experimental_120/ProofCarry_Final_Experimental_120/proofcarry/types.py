from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional

class Decision(str, Enum):
    CONTINUE = "CONTINUE"
    REJECT = "REJECT"

class RejectReason(str, Enum):
    MISSING_FACT = "MISSING_FACT"
    CONTRADICTORY_FACT = "CONTRADICTORY_FACT"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    EXPIRED_CERTIFICATE = "EXPIRED_CERTIFICATE"
    NONCE_REUSE = "NONCE_REUSE"
    WRONG_EXECUTION = "WRONG_EXECUTION"
    WRONG_WORKFLOW = "WRONG_WORKFLOW"
    WRONG_RUNTIME = "WRONG_RUNTIME"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INCOMPLETE_SNAPSHOT = "INCOMPLETE_SNAPSHOT"
    DEPENDENCY_UNRESOLVED = "DEPENDENCY_UNRESOLVED"
    INVALID_CERTIFICATE = "INVALID_CERTIFICATE"
    UNAUTHORIZED_ISSUER = "UNAUTHORIZED_ISSUER"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"

@dataclass(frozen=True)
class RuntimeContext:
    workflow_id: str
    execution_id: str
    source_runtime: str
    target_runtime: str
    contract_hash: str

@dataclass
class Resolution:
    decision: Decision
    plan: Optional[str]
    reason: Optional[str]
    resolved_facts: Dict[str, Any] = field(default_factory=dict)
    rejected_evidence: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        d["decision"] = self.decision.value
        return d
