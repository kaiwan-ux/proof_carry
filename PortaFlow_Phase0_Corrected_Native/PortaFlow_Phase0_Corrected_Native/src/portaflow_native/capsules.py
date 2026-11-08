from __future__ import annotations
from typing import Any
from .models import SourceCapture, LogicalState


def _history_view(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out=[]
    for e in trace:
        if e.get("kind") == "effect_committed":
            out.append({"seq":e.get("seq"),"kind":"tool_call_observed","step":e.get("step"),"detail":{"commit_status":"unknown"}})
        else:
            out.append(dict(e))
    return out


def export_capsule(capture: SourceCapture, condition: str) -> dict[str, Any]:
    s=capture.state
    base={
        "workflow": s["workflow"], "request_id": s["request_id"],
        "amount": s.get("amount",100), "max_retries": s.get("max_retries",2),
    }
    if condition == "naive_state":
        return {"condition":condition,"payload":base}
    if condition == "state_history":
        return {"condition":condition,"payload":{**base,"completed":list(s.get("completed",[])),"trace":_history_view(s.get("trace",[]))}}
    if condition == "native_semantic":
        # Diagnostic upper bound only. This is NOT PortaFlow/PCC and must not be claimed as a proposed method.
        return {"condition":condition,"payload":{**base,"completed":list(s.get("completed",[])),"trace":list(s.get("trace",[])),
            "retry_attempts":s.get("retry_attempts",0),"pending_approval":s.get("pending_approval",False),
            "approved":s.get("approved"),"effect_receipts":dict(s.get("effect_receipts",{})),
            "source_native_snapshot":capture.native_snapshot}}
    raise KeyError(condition)


def import_capsule(capsule: dict[str, Any]) -> LogicalState:
    condition=capsule["condition"]; p=capsule["payload"]
    s=LogicalState(workflow=p["workflow"],request_id=p["request_id"],amount=int(p.get("amount",100)),max_retries=int(p.get("max_retries",2)))
    if condition in {"state_history","native_semantic"}:
        s.completed=list(p.get("completed",[])); s.trace=[dict(x) for x in p.get("trace",[])]
    if condition == "state_history":
        for e in s.trace:
            if e.get("kind") == "tool_attempt_failed": s.retry_attempts=max(s.retry_attempts,int(e.get("detail",{}).get("attempt",0)))
            elif e.get("kind") == "approval_requested": s.pending_approval=True
            elif e.get("kind") == "approval_response": s.pending_approval=False; s.approved=bool(e.get("detail",{}).get("approved"))
        # Intentionally cannot infer committed external effect from tool_call_observed.
    elif condition == "native_semantic":
        s.retry_attempts=int(p.get("retry_attempts",0)); s.pending_approval=bool(p.get("pending_approval",False))
        s.approved=p.get("approved"); s.effect_receipts=dict(p.get("effect_receipts",{}))
    return s
