from __future__ import annotations

from .models import Capsule, RuntimeState, Event


def export_capsule(state: RuntimeState, condition: str) -> Capsule:
    if condition == "naive_state":
        payload = {
            "workflow": state.workflow,
            "variant": state.variant,
            "vars": dict(state.vars),
            "current_step": state.current_step,
        }
    elif condition == "state_history":
        payload = {
            "workflow": state.workflow,
            "variant": state.variant,
            "vars": dict(state.vars),
            "current_step": state.current_step,
            "completed": list(state.completed),
            # User-visible history baseline: preserve observable execution history but
            # intentionally do not expose privileged effect-commit knowledge. A crash
            # after a tool call can make "called" vs "committed" ambiguous.
            "trace": [_history_view(e.to_dict()) for e in state.trace],
        }
    elif condition == "oracle_full":
        payload = state.to_dict()
    elif condition == "restart":
        payload = {"workflow": state.workflow, "variant": state.variant}
    else:
        raise KeyError(condition)
    return Capsule(condition=condition, payload=payload)


def import_capsule(capsule: Capsule) -> RuntimeState:
    p = capsule.payload
    condition = capsule.condition
    if condition == "oracle_full":
        trace = [Event(**e) for e in p.get("trace", [])]
        return RuntimeState(
            workflow=p["workflow"], variant=p["variant"], vars=dict(p.get("vars", {})),
            current_step=p.get("current_step", "start"), completed=list(p.get("completed", [])), trace=trace,
            effects=dict(p.get("effects", {})), branch_choice=p.get("branch_choice"),
            loop_iteration=int(p.get("loop_iteration", 0)), retry_attempts=int(p.get("retry_attempts", 0)),
            pending_approval=bool(p.get("pending_approval", False)), approved=p.get("approved"),
            terminated=bool(p.get("terminated", False)), outcome=p.get("outcome"),
        )

    s = RuntimeState(workflow=p["workflow"], variant=p["variant"])
    s.vars = dict(p.get("vars", {}))
    s.current_step = p.get("current_step", "start")

    if condition == "state_history":
        s.completed = list(p.get("completed", []))
        s.trace = [Event(**e) for e in p.get("trace", [])]
        _infer_from_history(s)
    return s


def _history_view(e: dict) -> dict:
    if e.get("kind") == "effect_committed":
        return {"seq": e.get("seq", 0), "kind": "tool_call_observed", "step": e.get("step", "tool"), "detail": {"commit_status": "unknown"}}
    return e


def _infer_from_history(s: RuntimeState) -> None:
    """Best-effort history baseline, deliberately generic and transparent.

    It can infer some semantics from observable events but not privileged runtime state.
    """
    for e in s.trace:
        if e.kind == "tool_attempt_failed":
            s.retry_attempts = max(s.retry_attempts, int(e.detail.get("attempt", 0)))
        elif e.kind == "approval_requested":
            s.pending_approval = True
        elif e.kind == "approval_response":
            s.pending_approval = False
            s.approved = bool(e.detail.get("approved"))
        elif e.kind == "effect_committed":
            # Kept for compatibility with explicitly privileged traces; the standard
            # state_history baseline masks this event to tool_call_observed.
            s.effects[e.step] = max(s.effects.get(e.step, 0), int(e.detail.get("count", 1)))
    # Loop progress is reconstructable from completed logical step names.
    loops = [x for x in s.completed if x.startswith("loop_") and x.split("_")[-1].isdigit()]
    if loops:
        s.loop_iteration = max(int(x.split("_")[-1]) for x in loops)
    if "decision" in s.vars:
        s.branch_choice = s.vars["decision"]
