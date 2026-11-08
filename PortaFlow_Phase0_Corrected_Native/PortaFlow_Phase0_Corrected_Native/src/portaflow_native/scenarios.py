from __future__ import annotations
from .models import LogicalState

REQUIRED = {
    "retry": ["start", "tool_fail_1", "tool_success_2", "finish"],
    "approval": ["prepare", "wait_approval", "execute", "finish"],
    "side_effect": ["prepare", "payment", "verify", "finish"],
}
PREFIX = {
    "retry": ["start", "tool_fail_1"],
    "approval": ["prepare", "wait_approval"],
    "side_effect": ["prepare", "payment"],
}


def initial_state(workflow: str) -> LogicalState:
    return LogicalState(workflow=workflow, request_id=f"pf-{workflow}-001", amount=100, max_retries=2)


def source_prefix_transition(state: LogicalState, ledger: dict[str, int]) -> LogicalState:
    s=state.clone()
    if s.workflow == "retry":
        s.step("start")
        s.retry_attempts = 1
        s.event("tool_attempt_failed", "tool", attempt=1)
        s.step("tool_fail_1")
    elif s.workflow == "approval":
        s.step("prepare")
        s.pending_approval = True
        s.event("approval_requested", "wait_approval", request_id="approval-001")
        s.step("wait_approval")
    elif s.workflow == "side_effect":
        s.step("prepare")
        ledger["payment"] = ledger.get("payment", 0) + 1
        s.effect_receipts["payment"] = True
        s.event("effect_committed", "payment", operation_id=s.request_id, count=ledger["payment"])
        s.step("payment")
    else:
        raise KeyError(s.workflow)
    return s


def continuation_transition(state: LogicalState, ledger: dict[str, int]) -> LogicalState:
    s=state.clone()
    if s.workflow == "retry":
        # Missing retry semantics makes the target perform failed attempt #1 again.
        if s.retry_attempts < 1:
            s.retry_attempts = 1
            s.event("tool_attempt_failed", "tool", attempt=1)
            s.step("tool_fail_1")
        s.retry_attempts = 2
        s.event("tool_attempt_succeeded", "tool", attempt=2)
        s.step("tool_success_2")
        s.step("finish")
        s.terminated=True; s.outcome="done"
    elif s.workflow == "approval":
        if s.pending_approval:
            s.event("approval_response", "wait_approval", approved=True)
            s.pending_approval=False; s.approved=True
        # If the pending request was lost, execution proceeds without consuming approval.
        s.step("execute")
        s.step("finish")
        s.terminated=True; s.outcome="approved_and_done"
    elif s.workflow == "side_effect":
        if not s.effect_receipts.get("payment", False):
            ledger["payment"] = ledger.get("payment",0) + 1
            s.effect_receipts["payment"] = True
            s.event("effect_committed", "payment", operation_id=s.request_id, count=ledger["payment"])
            s.step("payment")
        s.step("verify")
        s.step("finish")
        s.terminated=True; s.outcome="done"
    else:
        raise KeyError(s.workflow)
    return s
