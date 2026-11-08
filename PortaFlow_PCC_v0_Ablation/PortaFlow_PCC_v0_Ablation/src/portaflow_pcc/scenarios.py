from __future__ import annotations
from .models import LogicalState

WORKFLOWS = ["retry", "approval", "side_effect", "branch", "loop", "parallel"]

REQUIRED = {
    "retry": ["start", "tool_fail_1", "tool_success_2", "finish"],
    "approval": ["prepare", "wait_approval", "execute", "finish"],
    "side_effect": ["prepare", "payment", "verify", "finish"],
    "branch": ["start", "decision", "left_action", "finish"],
    "loop": ["start", "loop_body_1", "loop_body_2", "loop_body_3", "finish"],
    "parallel": ["start", "fanout", "branch_a", "branch_b", "join", "finish"],
}

PREFIX = {
    "retry": ["start", "tool_fail_1"],
    "approval": ["prepare", "wait_approval"],
    "side_effect": ["prepare", "payment"],
    "branch": ["start", "decision"],
    "loop": ["start", "loop_body_1", "loop_body_2"],
    "parallel": ["start", "fanout", "branch_a"],
}


def initial_state(workflow: str) -> LogicalState:
    return LogicalState(workflow=workflow, request_id=f"pcc-{workflow}-001", amount=100, max_retries=2)


def source_prefix_transition(state: LogicalState, ledger: dict[str, int]) -> LogicalState:
    s = state.clone()
    if s.workflow == "retry":
        s.step("start")
        s.retry_attempts = 1
        s.event("tool_attempt_failed", "tool", attempt=1)
        s.step("tool_fail_1")
        s.control_frontier = {"next": "tool_success_2", "phase": "retry"}
        s.pending_obligations = [{"type": "retry", "attempt": 2, "max_attempts": 2}]
    elif s.workflow == "approval":
        s.step("prepare")
        s.pending_approval = True
        s.approval_request_id = "approval-001"
        s.event("approval_requested", "wait_approval", request_id=s.approval_request_id)
        s.step("wait_approval")
        s.control_frontier = {"next": "execute", "blocked_on": "human_approval"}
        s.pending_obligations = [{"type": "human_approval", "request_id": s.approval_request_id}]
    elif s.workflow == "side_effect":
        s.step("prepare")
        ledger["payment"] = ledger.get("payment", 0) + 1
        s.effect_receipts["payment"] = {
            "operation_id": s.request_id,
            "status": "committed",
            "replay": "forbidden",
            "idempotency_key": f"idem-{s.request_id}",
        }
        s.event("effect_committed", "payment", operation_id=s.request_id, count=ledger["payment"])
        s.step("payment")
        s.control_frontier = {"next": "verify", "phase": "post_effect"}
    elif s.workflow == "branch":
        s.step("start")
        s.branch_choice = "left"
        s.event("branch_decided", "decision", choice="left")
        s.step("decision")
        s.control_frontier = {"next": "left_action", "branch_choice": "left"}
    elif s.workflow == "loop":
        s.step("start")
        s.loop_iteration = 1
        s.event("loop_iteration", "loop_body", iteration=1)
        s.step("loop_body_1")
        s.loop_iteration = 2
        s.event("loop_iteration", "loop_body", iteration=2)
        s.step("loop_body_2")
        s.control_frontier = {"next": "loop_body_3", "iteration": 3, "limit": 3}
    elif s.workflow == "parallel":
        s.step("start")
        s.step("fanout")
        s.parallel_completed = ["branch_a"]
        s.event("parallel_branch_completed", "branch_a", branch="a")
        s.step("branch_a")
        s.control_frontier = {"next": "parallel_resume", "join": "join"}
        s.pending_obligations = [{"type": "parallel_branch", "branch": "b"}]
        s.dependency_contract = {
            "join": "join",
            "requires": ["branch_a", "branch_b"],
            "exactly_once": ["branch_a", "branch_b"],
        }
    else:
        raise KeyError(s.workflow)
    return s


def continuation_transition(state: LogicalState, ledger: dict[str, int]) -> LogicalState:
    """Execute the remaining logical computation using only information imported into state.

    Missing semantic fields intentionally cause conservative/default recovery choices. The evaluator
    then checks whether those choices preserved the source execution contract.
    """
    s = state.clone()
    if s.workflow == "retry":
        if s.retry_attempts < 1:
            s.retry_attempts = 1
            s.event("tool_attempt_failed", "tool", attempt=1)
            s.step("tool_fail_1")
        s.retry_attempts = 2
        s.event("tool_attempt_succeeded", "tool", attempt=2)
        s.step("tool_success_2")
        s.step("finish")
        s.terminated = True; s.outcome = "done"

    elif s.workflow == "approval":
        has_pending = s.pending_approval or any(x.get("type") == "human_approval" for x in s.pending_obligations)
        if has_pending:
            rid = s.approval_request_id or next((x.get("request_id") for x in s.pending_obligations if x.get("type") == "human_approval"), None)
            s.event("approval_response", "wait_approval", approved=True, request_id=rid)
            s.pending_approval = False; s.approved = True
        s.step("execute")
        s.step("finish")
        s.terminated = True; s.outcome = "approved_and_done"

    elif s.workflow == "side_effect":
        receipt = s.effect_receipts.get("payment", {})
        committed = receipt.get("status") == "committed" and receipt.get("replay") == "forbidden"
        if not committed:
            ledger["payment"] = ledger.get("payment", 0) + 1
            s.effect_receipts["payment"] = {
                "operation_id": s.request_id, "status": "committed", "replay": "forbidden",
                "idempotency_key": f"target-{s.request_id}",
            }
            s.event("effect_committed", "payment", operation_id=s.request_id, count=ledger["payment"])
            s.step("payment")
        s.step("verify")
        s.step("finish")
        s.terminated = True; s.outcome = "done"

    elif s.workflow == "branch":
        choice = s.control_frontier.get("branch_choice") or s.branch_choice
        if choice not in {"left", "right"}:
            choice = "right"  # deterministic target default when branch decision is absent
        s.branch_choice = choice
        s.step(f"{choice}_action")
        s.step("finish")
        s.terminated = True; s.outcome = f"branch_{choice}_done"

    elif s.workflow == "loop":
        next_iter = s.control_frontier.get("iteration")
        if next_iter is None:
            # Without an explicit control frontier, restart loop body from iteration 1.
            for i in (1, 2, 3):
                s.loop_iteration = i
                s.event("loop_iteration", "loop_body", iteration=i)
                s.step(f"loop_body_{i}")
        else:
            for i in range(int(next_iter), 4):
                s.loop_iteration = i
                s.event("loop_iteration", "loop_body", iteration=i)
                s.step(f"loop_body_{i}")
        s.step("finish")
        s.terminated = True; s.outcome = "done"

    elif s.workflow == "parallel":
        contract = s.dependency_contract
        if contract.get("join") == "join" and contract.get("exactly_once"):
            already = set(s.parallel_completed)
            for branch in contract["requires"]:
                if branch not in already:
                    s.event("parallel_branch_completed", branch, branch=branch)
                    s.step(branch)
                    already.add(branch)
            s.parallel_completed = sorted(already)
        else:
            # Without the dependency/once-only contract, target conservatively recomputes both branches.
            for branch in ("branch_a", "branch_b"):
                s.event("parallel_branch_completed", branch, branch=branch)
                s.step(branch)
            s.parallel_completed = ["branch_a", "branch_b"]
        s.step("join")
        s.step("finish")
        s.terminated = True; s.outcome = "done"
    else:
        raise KeyError(s.workflow)
    return s
