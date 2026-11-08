from __future__ import annotations
from dataclasses import dataclass,field,asdict
from typing import Any
@dataclass
class Case:
    case_id:str; family:str; scenario_name:str; description:str; index:int; params:dict[str,Any]; source_plan:list[dict[str,Any]]; oracle_plan:list[dict[str,Any]]; truth_facts:list[dict[str,Any]]; continuation_contract:dict[str,Any]; drop_fact:dict[str,Any]; subjects:list[str]; variants:list[str]; variant_expectations:dict[str,str]
    def to_dict(self): return asdict(self)
@dataclass
class NativePause:
    framework:str; case_id:str; checkpoint_ref:str; native_kind:str; pending_work:list[str]; app_state:dict[str,Any]; native_observation:dict[str,Any]; source_store:dict[str,Any]
    def to_dict(self): return asdict(self)
@dataclass
class Row:
    run_id:str; study:str; source:str; target:str; case_id:str; family:str; condition:str; method:str; safe_completion:int=0; safe_rejection:int=0; unsafe_violation:int=0; technical_failure:int=0; reject_reason:str=''; failure_types:list[str]=field(default_factory=list); payload_bytes:int=0; payload_sha256:str=''; latency_ms:float=0.0; error:str=''
    def to_dict(self): return asdict(self)
