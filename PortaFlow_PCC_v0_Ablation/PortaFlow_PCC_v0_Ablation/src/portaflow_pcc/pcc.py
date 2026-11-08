from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import Any
from .models import SourceCapture, LogicalState

SCHEMA_VERSION = "0.1"
CONDITIONS = [
    "state_only",
    "state_history",
    "plus_control_frontier",
    "plus_pending_obligations",
    "plus_effect_receipts",
    "full_pcc_v0",
]

@dataclass
class PortableContinuationCapsule:
    schema_version: str
    condition: str
    workflow: str
    request_id: str
    application_state: dict[str, Any]
    semantic_history: list[dict[str, Any]] | None = None
    completed: list[str] | None = None
    control_frontier: dict[str, Any] | None = None
    pending_obligations: list[dict[str, Any]] | None = None
    effect_receipts: dict[str, dict[str, Any]] | None = None
    continuation_contract: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def byte_size(self) -> int:
        # Experimental condition label is not part of a deployable wire format. Omit absent optional
        # sections as a real serializer would, so the overhead metric reflects carried semantics.
        d = self.to_dict()
        d.pop("condition", None)
        d = {k: v for k, v in d.items() if v is not None}
        return len(json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _history_view(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Model ordinary portable execution history, deliberately excluding live handles/commit certainty.

    This is not arbitrary: generic logs often record that an action/request occurred but do not carry
    a resumable pending request handle or an exactly-once external commitment receipt.
    """
    out: list[dict[str, Any]] = []
    for e in trace:
        kind = e.get("kind")
        detail = dict(e.get("detail", {}))
        if kind == "effect_committed":
            out.append({"seq": e.get("seq"), "kind": "tool_call_observed", "step": e.get("step"), "detail": {"commit_status": "unknown"}})
        elif kind == "approval_requested":
            out.append({"seq": e.get("seq"), "kind": "approval_requested", "step": e.get("step"), "detail": {"request_id": None, "live_handle": False}})
        elif kind == "branch_decided":
            out.append({"seq": e.get("seq"), "kind": "decision_observed", "step": e.get("step"), "detail": {"choice": "redacted"}})
        elif kind == "loop_iteration":
            out.append({"seq": e.get("seq"), "kind": "loop_body_observed", "step": e.get("step"), "detail": {}})
        else:
            out.append(dict(e))
    return out


def build_capsule(capture: SourceCapture, condition: str) -> PortableContinuationCapsule:
    if condition not in CONDITIONS:
        raise KeyError(condition)
    s = LogicalState.from_dict(capture.state)
    cap = PortableContinuationCapsule(
        schema_version=SCHEMA_VERSION,
        condition=condition,
        workflow=s.workflow,
        request_id=s.request_id,
        application_state={"amount": s.amount, "max_retries": s.max_retries},
        provenance={"source_framework": capture.framework, "native_snapshot_kind": capture.native_snapshot.get("kind", "unknown")},
    )
    idx = CONDITIONS.index(condition)
    if idx >= 1:
        cap.semantic_history = _history_view(s.trace)
        cap.completed = list(s.completed)
    if idx >= 2:
        cap.control_frontier = dict(s.control_frontier)
        # Branch/loop progress are control semantics, not ordinary application state.
        if s.branch_choice is not None:
            cap.control_frontier["branch_choice"] = s.branch_choice
        if s.loop_iteration:
            cap.control_frontier.setdefault("source_loop_iteration", s.loop_iteration)
    if idx >= 3:
        cap.pending_obligations = [dict(x) for x in s.pending_obligations]
    if idx >= 4:
        cap.effect_receipts = {k: dict(v) for k, v in s.effect_receipts.items()}
    if idx >= 5:
        cap.continuation_contract = {
            "dependency_contract": dict(s.dependency_contract),
            "hard_invariants": ["no_prefix_replay", "no_duplicate_effect", "preserve_required_gate", "correct_termination"],
        }
    # Critical anti-cheating rule: native_snapshot itself is NEVER embedded in the PCC payload.
    return cap


def lower_capsule(cap: PortableContinuationCapsule) -> LogicalState:
    a = cap.application_state
    s = LogicalState(workflow=cap.workflow, request_id=cap.request_id, amount=int(a.get("amount", 100)), max_retries=int(a.get("max_retries", 2)))
    if cap.semantic_history is not None:
        s.trace = [dict(x) for x in cap.semantic_history]
        s.completed = list(cap.completed or [])
        # Recover retry count from portable history where it is explicit.
        for e in s.trace:
            if e.get("kind") == "tool_attempt_failed":
                s.retry_attempts = max(s.retry_attempts, int(e.get("detail", {}).get("attempt", 0)))
    if cap.control_frontier is not None:
        s.control_frontier = dict(cap.control_frontier)
        if "branch_choice" in s.control_frontier:
            s.branch_choice = s.control_frontier["branch_choice"]
        if "source_loop_iteration" in s.control_frontier:
            s.loop_iteration = int(s.control_frontier["source_loop_iteration"])
    if cap.pending_obligations is not None:
        s.pending_obligations = [dict(x) for x in cap.pending_obligations]
        for ob in s.pending_obligations:
            if ob.get("type") == "human_approval":
                s.pending_approval = True
                s.approval_request_id = ob.get("request_id")
            if ob.get("type") == "retry":
                s.retry_attempts = max(s.retry_attempts, int(ob.get("attempt", 1)) - 1)
    if cap.effect_receipts is not None:
        s.effect_receipts = {k: dict(v) for k, v in cap.effect_receipts.items()}
    if cap.continuation_contract is not None:
        s.dependency_contract = dict(cap.continuation_contract.get("dependency_contract", {}))
        if s.workflow == "parallel":
            # Completed parallel branches come from completed trace/state; contract states how to use them.
            s.parallel_completed = [x for x in s.completed if x in {"branch_a", "branch_b"}]
    return s
