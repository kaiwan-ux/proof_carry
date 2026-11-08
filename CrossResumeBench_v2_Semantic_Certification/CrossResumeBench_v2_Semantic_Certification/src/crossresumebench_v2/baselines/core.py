from __future__ import annotations
import hashlib, json
from pathlib import Path
from ..models import TransferPackage, ReconstructedContinuation
from ..mcc import build_mcc_v2,reconstruct_mcc_v2,admissibility
from .history_baseline import infer_history_only
from .aaif_reference import project as aaif_project, lower as aaif_lower
from .caplease_reference import effect_ledger_from_certificates, lower as caplease_lower

BASELINES=["state_only","raw_history","history_inference","aaif_reference","caplease_reference","aaif_plus_caplease_reference","explicit_minimal","full_pcc","mcc_v2","oracle"]

def _truth_effects(capture):
    return {op:{"status":"committed","source":"oracle_source_ledger"} for op,count in capture.source_ledger.items() if int(count)>0}

def _wf_hash(case): return hashlib.sha256(json.dumps({"target_actions":case.target_actions,"dependencies":case.target_dependencies},sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_transfer(name,capture,case,target_runtime,root:Path):
    if name=="mcc_v2": return build_mcc_v2(capture,target_runtime,_wf_hash(case),root)
    if name=="state_only": return TransferPackage(name,{"case_id":capture.case_id,"workflow":capture.workflow,"app_state":capture.app_state})
    if name=="raw_history": return TransferPackage(name,{"case_id":capture.case_id,"workflow":capture.workflow,"app_state":capture.app_state,"history":capture.portable_history})
    if name=="history_inference": return TransferPackage(name,{"case_id":capture.case_id,"workflow":capture.workflow,"app_state":capture.app_state,"history":capture.portable_history})
    if name=="aaif_reference": return TransferPackage(name,aaif_project(capture,case))
    if name=="caplease_reference": return TransferPackage(name,{"app_state":capture.app_state,"effect_ledger":effect_ledger_from_certificates(capture)})
    if name=="aaif_plus_caplease_reference":
        p=aaif_project(capture,case); p["effect_ledger"]=effect_ledger_from_certificates(capture); return TransferPackage(name,p)
    if name=="explicit_minimal":
        return TransferPackage(name,{"app_state":capture.app_state,"completed_units":capture.truth_completed_units,"pending_obligations":capture.truth_pending_obligations,"effect_facts":_truth_effects(capture),"dependencies":capture.truth_dependencies,"decisions":capture.truth_decisions,"counters":capture.truth_counters})
    if name=="full_pcc": return TransferPackage(name,{"capture":capture.to_dict()})
    if name=="oracle": return TransferPackage(name,{"oracle":True,"capture":capture.to_dict()})
    raise KeyError(name)

def lower_transfer(pkg,capture,case,root:Path):
    n=pkg.name; p=pkg.payload
    if n=="mcc_v2":
        rc,rep=reconstruct_mcc_v2(p,case,root); pkg.inference_report=rep; ok,reason=admissibility(rc)
        if not ok: pkg.accepted=False; pkg.reject_reason=reason; return None
        return rc
    if n=="history_inference":
        rc,rep=infer_history_only(capture,case); pkg.inference_report=rep
        if rc.ambiguities: pkg.accepted=False; pkg.reject_reason=";".join(sorted({a['type'] for a in rc.ambiguities})); return None
        return rc
    if n=="state_only": return ReconstructedContinuation(capture.case_id,capture.workflow,dict(p["app_state"]))
    if n=="raw_history": return ReconstructedContinuation(capture.case_id,capture.workflow,dict(p["app_state"]))
    if n=="aaif_reference":
        rc=aaif_lower(p,capture,case,{})
        # Independent strict policy: ambiguous tool observations cause safe rejection.
        if any(e.get("type")=="tool_call_observed" and e.get("data",{}).get("commit_status")=="unknown" for e in p.get("conversation",[])):
            pkg.accepted=False; pkg.reject_reason="AAIF_REFERENCE_AMBIGUOUS_PENDING_EFFECT"; return None
        return rc
    if n=="caplease_reference": return caplease_lower(capture,case)
    if n=="aaif_plus_caplease_reference": return aaif_lower(p,capture,case,p.get("effect_ledger",{}))
    if n=="explicit_minimal": return ReconstructedContinuation(capture.case_id,capture.workflow,dict(p["app_state"]),list(p["completed_units"]),list(p["pending_obligations"]),dict(p["effect_facts"]),dict(p["dependencies"]),dict(p["decisions"]),dict(p["counters"]))
    if n in {"full_pcc","oracle"}:
        c=p["capture"]; return ReconstructedContinuation(capture.case_id,capture.workflow,dict(c["app_state"]),list(c["truth_completed_units"]),list(c["truth_pending_obligations"]),_truth_effects(capture),dict(c["truth_dependencies"]),dict(c["truth_decisions"]),dict(c["truth_counters"]))
    raise KeyError(n)
