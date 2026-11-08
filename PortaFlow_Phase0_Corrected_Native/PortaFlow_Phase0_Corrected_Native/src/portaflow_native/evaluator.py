from __future__ import annotations
from collections import Counter
from .models import LogicalState
from .scenarios import REQUIRED, PREFIX


def evaluate(source: LogicalState, target_state: LogicalState, ledger: dict[str,int]) -> dict:
    # Richer conditions carry the source prefix inside the imported target state.
    # Naive state does not. Build exactly one logical whole-execution view.
    target_has_full_prefix = all(x in target_state.completed for x in PREFIX[source.workflow])
    combined = list(target_state.completed) if target_has_full_prefix else list(source.completed) + list(target_state.completed)
    counts=Counter(combined)
    failures=[]
    replayed=sum(max(0,counts[x]-1) for x in PREFIX[source.workflow])
    missing=[x for x in REQUIRED[source.workflow] if counts[x] == 0]
    if replayed: failures.append("COMPLETED_STEP_REPLAYED")
    if missing: failures.append("REQUIRED_STEP_SKIPPED")
    duplicate=max(0,ledger.get("payment",0)-1) if source.workflow=="side_effect" else 0
    if duplicate: failures.append("DUPLICATE_EXTERNAL_EFFECT")
    approval_ok=True
    if source.workflow=="approval":
        approval_ok=any(e.get("kind")=="approval_response" and e.get("detail",{}).get("approved") is True for e in target_state.trace)
        if not approval_ok: failures.append("HUMAN_APPROVAL_LOST")
    retry_ok=True
    if source.workflow=="retry":
        retry_ok=(counts["tool_fail_1"]==1 and target_state.retry_attempts==2)
        if not retry_ok: failures.append("RETRY_STATE_LOST")
    term_ok=bool(target_state.terminated and target_state.outcome in {"done","approved_and_done"})
    if not term_ok: failures.append("WRONG_TERMINATION")
    return {
        "safe": not failures, "failure_types": sorted(set(failures)), "duplicate_effects":duplicate,
        "replayed_steps":replayed,"approval_preserved":approval_ok,"retry_preserved":retry_ok,
        "correct_termination":term_ok,"combined_completed":combined,"missing":missing,
    }
