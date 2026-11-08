from __future__ import annotations
from .models import CaseSpec, ActionSpec, SourceCapture
from .certificates import issue_certificate


def init_source(case: CaseSpec) -> dict:
    return {
        "history": [], "certificates": [], "ledger": {}, "completed": [], "pending": [],
        "dependencies": dict(case.target_dependencies), "decisions": {}, "counters": {},
    }


def _event(ctx, typ, action, **data):
    ctx["history"].append({
        "seq": len(ctx["history"]) + 1,
        "type": typ,
        "step": action.action_id,
        "semantic_unit": action.semantic_unit,
        "data": data,
    })


def apply_source_action(ctx: dict, raw_action: dict, case: CaseSpec) -> dict:
    a = ActionSpec.from_dict(raw_action)
    m = a.metadata
    completed = ctx["completed"]
    if a.kind == "step":
        _event(ctx, "step_observed", a, source_label=a.action_id)
        unit_completed = bool(m.get("unit_completed", True))
        if unit_completed and m.get("emit_completion", True):
            _event(ctx, "semantic_unit_completed", a, unit=a.semantic_unit)
        if unit_completed and a.semantic_unit not in completed:
            completed.append(a.semantic_unit)
        if unit_completed and m.get("certify_completion"):
            ctx["certificates"].append(issue_certificate(
                case.case_id, "semantic_completion", a.semantic_unit, "completed",
                m.get("scope", a.parent_unit or a.semantic_unit),
                {"native_marker": a.action_id, "reason": m.get("certificate_reason", "native_step_boundary")},
            ).to_dict())
    elif a.kind == "effect":
        op = a.operation or a.action_id
        actual_commit = bool(m.get("actual_commit", True))
        if actual_commit:
            ctx["ledger"][op] = ctx["ledger"].get(op, 0) + 1
        observed = m.get("observed_commit", "unknown")
        _event(ctx, "tool_call_observed", a, operation=op, commit_status=observed,
               result=m.get("result", "timeout"), parent_unit=a.parent_unit,
               unit_completion_observable=bool(m.get("emit_completion", False)))
        if m.get("certify_effect", True):
            ctx["certificates"].append(issue_certificate(
                case.case_id, "effect_commitment", op,
                "committed" if actual_commit else "not_committed", a.semantic_unit,
                {"operation_id": f"{case.case_id}:{op}", "idempotency_key": f"idem:{case.case_id}:{op}",
                 "replay": "forbidden" if actual_commit else "allowed"},
            ).to_dict())
        if m.get("unit_completed", True):
            if a.semantic_unit not in completed:
                completed.append(a.semantic_unit)
            if m.get("emit_completion", False):
                _event(ctx, "semantic_unit_completed", a, unit=a.semantic_unit)
            if m.get("certify_completion", False):
                ctx["certificates"].append(issue_certificate(
                    case.case_id, "semantic_completion", a.semantic_unit, "completed",
                    a.parent_unit or a.semantic_unit,
                    {"operation": op, "native_marker": a.action_id,
                     "reason": m.get("certificate_reason", "effect_and_postconditions_completed")},
                ).to_dict())
    elif a.kind == "approval":
        ob = {"type": "approval", "id": m.get("request_id", a.action_id), "blocks": m.get("blocks", a.semantic_unit)}
        ctx["pending"].append(ob)
        _event(ctx, "approval_requested", a, request_id=ob["id"], blocks=ob["blocks"])
        if m.get("certify_obligation"):
            ctx["certificates"].append(issue_certificate(
                case.case_id, "obligation_state", ob["id"], "pending", a.semantic_unit,
                {"kind": "approval", "blocks": ob["blocks"]},
            ).to_dict())
    elif a.kind == "callback":
        ob = {"type": "callback", "id": m.get("callback_id", a.action_id), "operation": a.operation}
        ctx["pending"].append(ob)
        _event(ctx, "callback_pending", a, callback_id=ob["id"], operation=a.operation)
    elif a.kind == "compensation":
        ob = {"type": "compensation", "action": a.semantic_unit, "effect": a.operation}
        ctx["pending"].append(ob)
        _event(ctx, "compensation_required", a, effect=a.operation, compensation_action=a.semantic_unit)
    elif a.kind == "join":
        _event(ctx, "join_observed", a, requires=a.depends_on)
        if m.get("completed", False) and a.semantic_unit not in completed:
            completed.append(a.semantic_unit)
    if "decision" in m:
        k, v = m["decision"]
        ctx["decisions"][k] = v
        _event(ctx, "decision_made", a, key=k, choice=v)
    if "counter" in m:
        k, v = m["counter"]
        ctx["counters"][k] = v
        _event(ctx, "counter_observed", a, key=k, value=v)
    if "retry" in m:
        attempt, maximum = m["retry"]
        _event(ctx, "retry_failed", a, attempt=attempt, max_attempts=maximum)
        ctx["pending"].append({"type": "retry", "step": a.semantic_unit,
                               "next_attempt": attempt + 1, "max_attempts": maximum})
    return ctx


def finalize_source(ctx: dict, case: CaseSpec, native_observation: dict | None = None) -> SourceCapture:
    return SourceCapture(
        case.case_id, case.family, dict(case.app_state), list(ctx["history"]), list(ctx["certificates"]),
        dict(ctx["ledger"]), native_observation or {"kind": "semantic_simulator", "framework": "semantic"},
        list(ctx["completed"]), list(ctx["pending"]), dict(ctx["dependencies"]),
        dict(ctx["decisions"]), dict(ctx["counters"]),
    )


def simulate_source(case: CaseSpec, native_observation: dict | None = None) -> SourceCapture:
    ctx = init_source(case)
    for raw in case.source_actions:
        apply_source_action(ctx, raw, case)
    return finalize_source(ctx, case, native_observation)
