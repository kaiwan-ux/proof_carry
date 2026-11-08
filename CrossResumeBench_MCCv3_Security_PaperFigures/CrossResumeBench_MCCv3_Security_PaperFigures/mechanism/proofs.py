from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class ProofState:
    facts: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, list[str]] = field(default_factory=dict)
    bindings: dict[str, str] = field(default_factory=dict)
    unresolved: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    invalid_attestations: list[str] = field(default_factory=list)
    def key(self, fact_type:str, subject:str)->str: return f"{fact_type}|{subject}"
    def get(self, fact_type:str, subject:str, default=None): return self.facts.get(self.key(fact_type,subject), default)
    def to_dict(self): return asdict(self)

def contract_hash(contract:dict)->str:
    import hashlib,json
    body=json.dumps(contract,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()
