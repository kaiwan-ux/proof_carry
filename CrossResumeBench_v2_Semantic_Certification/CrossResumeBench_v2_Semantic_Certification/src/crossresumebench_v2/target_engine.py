from __future__ import annotations
from .models import ActionSpec, ReconstructedContinuation, TargetResult


def init_target(continuation: ReconstructedContinuation, ledger: dict[str, int]) -> dict:
    return {
        "completed": list(continuation.completed_units), "executed": [], "ledger": dict(ledger),
        "pending": list(continuation.pending_obligations), "dependencies": {k: list(v) for k, v in continuation.dependencies.items()},
        "effect_facts": dict(continuation.effect_facts), "outcome": "done", "terminated": False,
    }


def apply_target_action(ctx: dict, raw_action: dict) -> dict:
    a = ActionSpec.from_dict(raw_action)
    completed = set(ctx["completed"])
    unit = a.semantic_unit
    if unit in completed:
        return ctx
    completes = bool(a.metadata.get("completes_unit", True))
    if a.kind == "effect":
        op = a.operation or a.action_id
        fact = ctx["effect_facts"].get(op, {}).get("status")
        if fact == "committed":
            ctx["executed"].append(f"reconcile:{unit}")
        else:
            ctx["ledger"][op] = ctx["ledger"].get(op, 0) + 1
            ctx["executed"].append(unit)
        if completes:
            completed.add(unit)
    elif a.kind == "approval":
        has = any(o.get("type") == "approval" and (o.get("blocks") == unit or o.get("id") == a.metadata.get("request_id")) for o in ctx["pending"])
        ctx["executed"].append(unit if has else f"approval_without_obligation:{unit}")
        if completes:
            completed.add(unit)
    elif a.kind == "callback":
        has = any(o.get("type") == "callback" and o.get("operation") == a.operation for o in ctx["pending"])
        ctx["executed"].append(unit if has else f"callback_without_obligation:{unit}")
        if completes:
            completed.add(unit)
    elif a.kind == "compensation":
        ctx["executed"].append(unit)
        completed.add(unit)
        if a.operation:
            key = f"compensate:{a.operation}"
            ctx["ledger"][key] = ctx["ledger"].get(key, 0) + 1
    elif a.kind == "join":
        req = set(ctx["dependencies"].get(unit, a.depends_on))
        missing = req - completed
        if missing:
            ctx["executed"].append(f"join_before:{','.join(sorted(missing))}")
            ctx["outcome"] = "dependency_violation"
        else:
            ctx["executed"].append(unit)
        completed.add(unit)
    elif a.kind == "finish":
        ctx["executed"].append(unit)
        completed.add(unit)
        ctx["terminated"] = True
    else:
        ctx["executed"].append(unit)
        if completes:
            completed.add(unit)
    ctx["completed"] = sorted(completed)
    return ctx


def finalize_target(ctx: dict, native_artifact=None) -> TargetResult:
    if not ctx["terminated"]:
        ctx["terminated"] = True
    return TargetResult(list(ctx["completed"]), list(ctx["executed"]), dict(ctx["ledger"]),
                        ctx["outcome"], bool(ctx["terminated"]), native_artifact or {"kind": "semantic_target"})


def execute_target(case, rc: ReconstructedContinuation, ledger: dict[str, int], native_artifact=None) -> TargetResult:
    ctx = init_target(rc, ledger)
    for raw in case.target_actions:
        apply_target_action(ctx, raw)
    return finalize_target(ctx, native_artifact)
