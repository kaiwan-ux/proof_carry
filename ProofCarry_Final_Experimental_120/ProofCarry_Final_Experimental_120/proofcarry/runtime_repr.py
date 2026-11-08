from __future__ import annotations
from typing import Dict, Any, Tuple, Optional

PREFIX = {
    "langgraph": "node",
    "crewai": "task",
    "maf": "handler",
}

def native_id(runtime: str, case_id: str, semantic_unit: str) -> str:
    return f"{PREFIX[runtime]}::{case_id}::{semantic_unit}"

def build_runtime_state(case: Dict[str, Any], runtime: str) -> Dict[str, Any]:
    return {
        "runtime": runtime,
        "case_id": case["case_id"],
        "workflow_id": case["workflow_id"],
        "execution_id": case["execution_id"],
        "checkpoint_id": f"ckpt::{runtime}::{case['case_id']}",
        "task_id": native_id(runtime, case["case_id"], case["required_identity"]),
        "pending_state": case["pending_state"],
        "retry_state": case.get("runtime_state",{}).get("retry_state"),
        "callback_state": case.get("runtime_state",{}).get("callback_state"),
        "branch_state": case.get("runtime_state",{}).get("branch_state"),
        "approval_state": case.get("runtime_state",{}).get("approval_state"),
    }

def identity_mapping(case: Dict[str, Any], source: str, target: str, mode: str="correct") -> Dict[str, Any]:
    sem=case["required_identity"]
    src=native_id(source, case["case_id"], sem)
    tgt=native_id(target, case["case_id"], sem)
    if mode == "correct":
        return {"semantic":sem,"source_id":src,"target_id":tgt,"status":"unique"}
    if mode == "missing":
        return {"semantic":sem,"source_id":src,"target_id":None,"status":"missing"}
    if mode == "wrong":
        return {"semantic":sem,"source_id":src,"target_id":native_id(target, case["case_id"], "wrong_unit"),"status":"wrong"}
    if mode == "ambiguous":
        return {"semantic":sem,"source_id":src,"target_id":[tgt, native_id(target, case["case_id"], "alternate_unit")],"status":"ambiguous"}
    raise ValueError(mode)

def validate_mapping(case: Dict[str, Any], source: str, target: str, mapping: Dict[str, Any]) -> bool:
    sem=case["required_identity"]
    return (
        mapping.get("status") == "unique" and
        mapping.get("semantic") == sem and
        mapping.get("source_id") == native_id(source, case["case_id"], sem) and
        mapping.get("target_id") == native_id(target, case["case_id"], sem)
    )
