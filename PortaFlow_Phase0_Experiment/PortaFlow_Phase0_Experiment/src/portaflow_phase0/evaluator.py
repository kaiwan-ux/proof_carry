from __future__ import annotations

from collections import Counter

from .models import Evaluation, RuntimeState
from .workflows import spec


def evaluate(prefix: RuntimeState, final: RuntimeState) -> Evaluation:
    sp = spec(prefix.workflow)
    inv: dict[str, bool] = {}
    failures: list[str] = []
    notes: list[str] = []

    final_counts = Counter(final.completed)
    prefix_counts = Counter(prefix.completed)

    required_ok = all(step in final_counts for step in sp.required_steps)
    inv["required_steps"] = required_ok
    if not required_ok:
        failures.append("REQUIRED_STEP_SKIPPED")

    replayed = []
    for step in sp.forbidden_replay_before_boundary:
        # In a correctly continued trace, prefix steps appear once overall. Since final state imported from
        # a capsule may or may not contain prefix history, compare execution count above prefix count when possible.
        if final_counts[step] > max(1, prefix_counts[step]):
            replayed.append(step)
    # Restart baseline has no imported prefix history. Detect replay by condition notes injected by runner.
    inv["no_forbidden_replay"] = not replayed
    if replayed:
        failures.append("COMPLETED_STEP_REPLAYED")
        notes.append("replayed=" + ",".join(replayed))

    inv["correct_termination"] = final.terminated and final.outcome == sp.expected_outcome
    if not inv["correct_termination"]:
        failures.append("WRONG_TERMINATION")

    if prefix.workflow == "branch":
        inv["branch_preserved"] = final.outcome == "approved" and (final.branch_choice or final.vars.get("decision")) == "approved_path"
        if not inv["branch_preserved"]:
            failures.append("BRANCH_DECISION_LOST")

    if prefix.workflow == "loop":
        inv["loop_progress_preserved"] = final.loop_iteration == 3
        if not inv["loop_progress_preserved"]:
            failures.append("LOOP_PROGRESS_LOST")

    if prefix.workflow == "retry":
        # Must succeed on second logical attempt, preserving one prior failure.
        inv["retry_preserved"] = final.retry_attempts == 2
        if not inv["retry_preserved"]:
            failures.append("RETRY_OBLIGATION_LOST")

    if prefix.workflow == "approval":
        requested = any(e.kind == "approval_requested" for e in final.trace)
        responded = any(e.kind == "approval_response" for e in final.trace)
        inv["approval_preserved"] = requested and responded and final.approved is True
        if not inv["approval_preserved"]:
            failures.append("HUMAN_APPROVAL_LOST")

    if prefix.workflow == "side_effect":
        inv["no_duplicate_effect"] = final.effects.get("mock_payment", 0) == 1
        if not inv["no_duplicate_effect"]:
            failures.append("DUPLICATE_EXTERNAL_EFFECT")

    safe = all(inv.get(x, True) for x in sp.hard_invariants)
    return Evaluation(safe=safe, invariant_results=inv, failure_types=sorted(set(failures)), notes=notes)


def count_replayed(prefix: RuntimeState, final: RuntimeState) -> int:
    pc = Counter(prefix.completed)
    fc = Counter(final.completed)
    return sum(max(0, fc[s] - max(1, pc[s])) for s in spec(prefix.workflow).forbidden_replay_before_boundary)


def count_skipped(final: RuntimeState) -> int:
    return sum(1 for s in spec(final.workflow).required_steps if s not in final.completed)
