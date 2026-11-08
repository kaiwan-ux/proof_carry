from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
@dataclass
class HoldoutCase:
    case_id:str; family:str; description:str; index:int; params:dict[str,Any]; source_plan:list[dict[str,Any]]; oracle_plan:list[dict[str,Any]]; continuation_contract:dict[str,Any]; variants:list[str]; variant_expectations:dict[str,str]; alias_subject:str|None=None; drop_fact:dict[str,str]|None=None
    def to_dict(self): return asdict(self)
@dataclass
class NativePause:
    framework:str; case_id:str; checkpoint_ref:str; native_kind:str; pending_work:list[str]; app_state:dict[str,Any]; native_observation:dict[str,Any]; source_store:dict[str,Any]
    def to_dict(self): return asdict(self)
@dataclass
class Row:
    run_id:str; source:str; target:str; case_id:str; family:str; evidence_variant:str; method:str; safe_completion:int=0; safe_rejection:int=0; unsafe_violation:int=0; technical_failure:int=0; reject_reason:str=''; failure_types:list[str]=field(default_factory=list); payload_bytes:int=0; payload_sha256:str=''; expected_plan:list[dict[str,Any]]=field(default_factory=list); actual_plan:list[dict[str,Any]]=field(default_factory=list); error:str=''
    def to_dict(self): return asdict(self)
