from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .models import TransferPackage, ReconstructedContinuation, SourceCapture
from .certificates import verify_certificate

FORBIDDEN_KEYS={"state","frontier","completed_units","completed_steps","native_checkpoint","source_native_snapshot","checkpoint_id","flow_id","thread_id","executor_state"}

def load_schema(root:Path): return json.loads((root/'schemas'/'mcc_v2.schema.json').read_text(encoding='utf-8'))

def validate_mcc_payload(payload:dict,root:Path):
    Draft202012Validator(load_schema(root)).validate(payload)
    def scan(x,path="$"):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in FORBIDDEN_KEYS: raise ValueError(f"forbidden MCC key {k!r} at {path}")
                scan(v,path+"."+k)
        elif isinstance(x,list):
            for i,v in enumerate(x): scan(v,f"{path}[{i}]")
    scan(payload)
    return True

def build_mcc_v2(capture:SourceCapture,target_runtime:str,workflow_spec_hash:str,root:Path)->TransferPackage:
    payload={
        "mcc_version":"2.0",
        "case_id":capture.case_id,
        "workflow":capture.workflow,
        "source_runtime":capture.native_observation.get("framework","semantic"),
        "target_runtime":target_runtime,
        "workflow_spec_hash":workflow_spec_hash,
        "app_state":capture.app_state,
        "history":capture.portable_history,
        "certificates":capture.certificates,
    }
    validate_mcc_payload(payload,root)
    return TransferPackage("mcc_v2",payload)

def reconstruct_mcc_v2(payload:dict,case,root:Path)->tuple[ReconstructedContinuation,dict]:
    validate_mcc_payload(payload,root)
    rc=ReconstructedContinuation(payload["case_id"],payload["workflow"],dict(payload.get("app_state",{})))
    ambiguous_effects=set(); ambiguous_units=set(); cert_log=[]
    # History inference is deliberately generic and target-side.
    for e in payload.get("history",[]):
        typ=e.get("type"); unit=e.get("semantic_unit") or e.get("data",{}).get("unit"); d=e.get("data",{})
        if typ=="semantic_unit_completed" and unit:
            if unit not in rc.completed_units: rc.completed_units.append(unit)
            rc.inference_log.append(f"history:completed:{unit}")
        elif typ=="tool_call_observed":
            op=d.get("operation") or e.get("step")
            if d.get("commit_status") in {"committed","not_committed"}:
                rc.effect_facts[op]={"status":d.get("commit_status"),"source":"history"}
            else:
                ambiguous_effects.add(op)
            if d.get("parent_unit") and not d.get("unit_completion_observable",False): ambiguous_units.add(unit)
        elif typ=="approval_requested":
            blocked=d.get("blocks") or unit
            rc.pending_obligations.append({"type":"approval","id":d.get("request_id"),"blocks":blocked})
            if blocked: ambiguous_units.discard(blocked)  # a live blocking obligation proves the unit is not complete
        elif typ=="callback_pending":
            rc.pending_obligations.append({"type":"callback","id":d.get("callback_id"),"operation":d.get("operation"),"blocks":unit})
            if unit: ambiguous_units.discard(unit)  # pending callback proves the enclosing unit remains open
        elif typ=="compensation_required":
            rc.pending_obligations.append({"type":"compensation","action":d.get("compensation_action") or unit,"effect":d.get("effect")})
        elif typ=="decision_made": rc.decisions[d.get("key","route")]=d.get("choice")
        elif typ=="counter_observed": rc.counters[d.get("key")]=int(d.get("value",0))
        elif typ=="retry_failed":
            rc.counters[f"retry:{unit}"]=int(d.get("attempt",0)); rc.pending_obligations.append({"type":"retry","step":unit,"next_attempt":int(d.get("attempt",0))+1,"max_attempts":int(d.get("max_attempts",0))})
        elif typ=="join_observed" and unit:
            rc.dependencies[unit]=list(d.get("requires",[]))
    for cert in payload.get("certificates",[]):
        if not verify_certificate(cert):
            rc.ambiguities.append({"type":"INVALID_CERTIFICATE","certificate_id":cert.get("certificate_id")}); continue
        ft,sub,val=cert.get("fact_type"),cert.get("subject"),cert.get("value")
        cert_log.append(f"{ft}:{sub}:{val}")
        if ft=="effect_commitment":
            rc.effect_facts[sub]={"status":val,"source":"certificate","evidence":cert.get("evidence",{})}; ambiguous_effects.discard(sub)
        elif ft=="semantic_completion" and val=="completed":
            if sub not in rc.completed_units: rc.completed_units.append(sub)
            ambiguous_units.discard(sub)
        elif ft=="obligation_state" and val=="pending":
            ev=cert.get("evidence",{}); rc.pending_obligations.append({"type":ev.get("kind","obligation"),"id":sub,"blocks":ev.get("blocks")})
        elif ft=="dependency_state":
            rc.dependencies[sub]=list(val if isinstance(val,list) else [])
    # Public target workflow structure supplies declared dependencies; this is not source-native state.
    for k,v in case.target_dependencies.items(): rc.dependencies.setdefault(k,list(v))
    # Only unresolved facts needed by the target create rejection-worthy ambiguity.
    target_ops={a.get("operation") for a in case.target_actions if a.get("kind")=="effect" and a.get("operation")}
    target_units={a.get("semantic_unit") for a in case.target_actions}
    for op in sorted(ambiguous_effects & target_ops): rc.ambiguities.append({"type":"AMBIGUOUS_EXTERNAL_COMMIT","operation":op})
    for unit in sorted(u for u in ambiguous_units if u in target_units and u not in rc.completed_units): rc.ambiguities.append({"type":"AMBIGUOUS_SEMANTIC_COMPLETION","semantic_unit":unit})
    report={"ambiguities":rc.ambiguities,"certificate_log":cert_log,"inference_log":rc.inference_log}
    return rc,report

def admissibility(rc:ReconstructedContinuation)->tuple[bool,str|None]:
    critical={"INVALID_CERTIFICATE","AMBIGUOUS_EXTERNAL_COMMIT","AMBIGUOUS_SEMANTIC_COMPLETION"}
    if any(a.get("type") in critical for a in rc.ambiguities):
        return False,";".join(sorted({a.get('type','UNKNOWN') for a in rc.ambiguities}))
    return True,None
