from __future__ import annotations
from collections import Counter
from .models import LogicalState
from .scenarios import REQUIRED, PREFIX


def evaluate(source: LogicalState, target_state: LogicalState, ledger: dict[str, int]) -> dict:
    target_has_prefix = all(x in target_state.completed for x in PREFIX[source.workflow])
    combined = list(target_state.completed) if target_has_prefix else list(source.completed) + list(target_state.completed)
    counts = Counter(combined)
    failures: list[str] = []
    replayed = sum(max(0, counts[x] - 1) for x in PREFIX[source.workflow])
    missing = [x for x in REQUIRED[source.workflow] if counts[x] == 0]
    if replayed:
        failures.append("COMPLETED_STEP_REPLAYED")
    if missing:
        failures.append("REQUIRED_STEP_SKIPPED")

    duplicate = max(0, ledger.get("payment", 0) - 1) if source.workflow == "side_effect" else 0
    if duplicate:
        failures.append("DUPLICATE_EXTERNAL_EFFECT")

    approval_ok = True
    if source.workflow == "approval":
        approval_ok = any(e.get("kind") == "approval_response" and e.get("detail", {}).get("approved") is True for e in target_state.trace)
        if not approval_ok:
            failures.append("HUMAN_APPROVAL_LOST")

    retry_ok = True
    if source.workflow == "retry":
        retry_ok = counts["tool_fail_1"] == 1 and target_state.retry_attempts == 2
        if not retry_ok:
            failures.append("RETRY_STATE_LOST")

    branch_ok = True
    if source.workflow == "branch":
        branch_ok = target_state.branch_choice == "left" and counts["left_action"] == 1 and counts["right_action"] == 0
        if not branch_ok:
            failures.append("BRANCH_DECISION_LOST")

    loop_ok = True
    if source.workflow == "loop":
        loop_ok = all(counts[f"loop_body_{i}"] == 1 for i in (1, 2, 3)) and target_state.loop_iteration == 3
        if not loop_ok:
            failures.append("LOOP_PROGRESS_LOST")

    parallel_ok = True
    if source.workflow == "parallel":
        parallel_ok = counts["branch_a"] == 1 and counts["branch_b"] == 1 and counts["join"] == 1
        if not parallel_ok:
            failures.append("PARALLEL_DEPENDENCY_LOST")

    term_ok = bool(target_state.terminated and target_state.outcome in {"done", "approved_and_done", "branch_left_done"})
    if not term_ok:
        failures.append("WRONG_TERMINATION")

    return {
        "safe": not failures,
        "failure_types": sorted(set(failures)),
        "duplicate_effects": duplicate,
        "replayed_steps": replayed,
        "approval_preserved": approval_ok,
        "retry_preserved": retry_ok,
        "branch_preserved": branch_ok,
        "loop_preserved": loop_ok,
        "parallel_preserved": parallel_ok,
        "correct_termination": term_ok,
        "combined_completed": combined,
        "missing": missing,
    }
