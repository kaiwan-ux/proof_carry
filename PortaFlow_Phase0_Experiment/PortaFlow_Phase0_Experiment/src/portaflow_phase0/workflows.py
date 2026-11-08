from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import RuntimeState


@dataclass(frozen=True)
class WorkflowSpec:
    name: str
    boundary: str
    required_steps: tuple[str, ...]
    forbidden_replay_before_boundary: tuple[str, ...]
    expected_outcome: str
    hard_invariants: tuple[str, ...]


def spec(name: str) -> WorkflowSpec:
    specs = {
        "linear": WorkflowSpec(
            "linear", "B", ("A", "B", "C", "D"), ("A", "B"), "done",
            ("required_steps", "no_forbidden_replay", "correct_termination"),
        ),
        "branch": WorkflowSpec(
            "branch", "decide", ("start", "decide", "approved_path", "finish"),
            ("start", "decide"), "approved",
            ("required_steps", "branch_preserved", "no_forbidden_replay", "correct_termination"),
        ),
        "loop": WorkflowSpec(
            "loop", "loop_2", ("init", "loop_1", "loop_2", "loop_3", "finish"),
            ("init", "loop_1", "loop_2"), "done",
            ("required_steps", "loop_progress_preserved", "no_forbidden_replay", "correct_termination"),
        ),
        "retry": WorkflowSpec(
            "retry", "tool_fail_1", ("start", "tool_fail_1", "tool_success_2", "finish"),
            ("start", "tool_fail_1"), "done",
            ("required_steps", "retry_preserved", "no_forbidden_replay", "correct_termination"),
        ),
        "approval": WorkflowSpec(
            "approval", "wait_approval", ("prepare", "wait_approval", "execute", "finish"),
            ("prepare", "wait_approval"), "approved_and_done",
            ("required_steps", "approval_preserved", "no_forbidden_replay", "correct_termination"),
        ),
        "side_effect": WorkflowSpec(
            "side_effect", "payment", ("prepare", "payment", "verify", "finish"),
            ("prepare", "payment"), "done",
            ("required_steps", "no_duplicate_effect", "no_forbidden_replay", "correct_termination"),
        ),
    }
    return specs[name]


def make_initial(name: str, variant: int) -> RuntimeState:
    s = RuntimeState(workflow=name, variant=variant)
    # Application-visible variables; intentionally not every execution obligation.
    s.vars = {
        "request_id": f"req-{name}-{variant}",
        "amount": 100 + variant,
        "branch_input": "approve",
        "loop_target": 3,
        "max_retries": 2,
    }
    return s


def run_prefix(name: str, variant: int) -> RuntimeState:
    s = make_initial(name, variant)
    if name == "linear":
        _step(s, "A"); _step(s, "B")
    elif name == "branch":
        _step(s, "start")
        s.branch_choice = "approved_path"
        s.vars["decision"] = "approved_path"  # ordinary app state often does contain this
        _step(s, "decide")
    elif name == "loop":
        _step(s, "init")
        for i in (1, 2):
            s.loop_iteration = i
            _step(s, f"loop_{i}")
    elif name == "retry":
        _step(s, "start")
        s.retry_attempts = 1
        s.emit("tool_attempt_failed", "tool", attempt=1)
        _step(s, "tool_fail_1")
    elif name == "approval":
        _step(s, "prepare")
        s.pending_approval = True
        s.emit("approval_requested", "wait_approval", request_id=f"approval-{variant}")
        _step(s, "wait_approval")
    elif name == "side_effect":
        _step(s, "prepare")
        s.effect("mock_payment")
        _step(s, "payment")
    else:
        raise KeyError(name)
    s.emit("migration_boundary", s.current_step)
    return s


def resume_from_state(s: RuntimeState) -> RuntimeState:
    """Continue from the semantic facts present in *s*.

    This is a framework-neutral controlled continuation model. It is not claimed
    to be native framework execution and is marked as controlled_model evidence.
    """
    name = s.workflow
    if name == "linear":
        if "C" not in s.completed: _step(s, "C")
        if "D" not in s.completed: _step(s, "D")
        _finish(s, "done")
    elif name == "branch":
        choice = s.branch_choice or s.vars.get("decision")
        if choice == "approved_path":
            if "approved_path" not in s.completed: _step(s, "approved_path")
            if "finish" not in s.completed: _step(s, "finish")
            _finish(s, "approved")
        else:
            _step(s, "rejected_path")
            _finish(s, "rejected")
    elif name == "loop":
        start = max(1, s.loop_iteration + 1)
        for i in range(start, int(s.vars.get("loop_target", 3)) + 1):
            s.loop_iteration = i
            _step(s, f"loop_{i}")
        if "finish" not in s.completed: _step(s, "finish")
        _finish(s, "done")
    elif name == "retry":
        # If attempts were lost, target thinks this is attempt 1 and will fail again.
        next_attempt = s.retry_attempts + 1
        if next_attempt <= 1:
            s.retry_attempts = 1
            s.emit("tool_attempt_failed", "tool", attempt=1)
            _step(s, "tool_fail_1")
            next_attempt = 2
        if next_attempt <= int(s.vars.get("max_retries", 2)):
            s.retry_attempts = next_attempt
            s.emit("tool_attempt_succeeded", "tool", attempt=next_attempt)
            _step(s, f"tool_success_{next_attempt}")
            _step(s, "finish")
            _finish(s, "done")
        else:
            _finish(s, "retry_exhausted")
    elif name == "approval":
        if s.pending_approval:
            s.emit("approval_response", "wait_approval", approved=True)
            s.pending_approval = False
            s.approved = True
        # If pending state was lost, this execution defaults to proceeding, which is a contract violation.
        if "execute" not in s.completed: _step(s, "execute")
        if "finish" not in s.completed: _step(s, "finish")
        _finish(s, "approved_and_done")
    elif name == "side_effect":
        # If committed effect information is absent, application cannot prove it happened and repeats it.
        if s.effects.get("mock_payment", 0) == 0:
            s.effect("mock_payment")
            _step(s, "payment")
        if "verify" not in s.completed: _step(s, "verify")
        if "finish" not in s.completed: _step(s, "finish")
        _finish(s, "done")
    else:
        raise KeyError(name)
    return s


def restart(name: str, variant: int) -> RuntimeState:
    s = make_initial(name, variant)
    if name == "linear":
        for x in ("A", "B", "C", "D"): _step(s, x)
        _finish(s, "done")
    elif name == "branch":
        _step(s, "start"); s.branch_choice = "approved_path"; s.vars["decision"] = "approved_path"; _step(s, "decide")
        _step(s, "approved_path"); _step(s, "finish"); _finish(s, "approved")
    elif name == "loop":
        _step(s, "init")
        for i in (1,2,3): s.loop_iteration=i; _step(s, f"loop_{i}")
        _step(s, "finish"); _finish(s, "done")
    elif name == "retry":
        _step(s, "start"); s.retry_attempts=1; s.emit("tool_attempt_failed", "tool", attempt=1); _step(s,"tool_fail_1")
        s.retry_attempts=2; s.emit("tool_attempt_succeeded", "tool", attempt=2); _step(s,"tool_success_2"); _step(s,"finish"); _finish(s,"done")
    elif name == "approval":
        _step(s,"prepare"); s.pending_approval=True; s.emit("approval_requested","wait_approval"); _step(s,"wait_approval")
        s.emit("approval_response","wait_approval",approved=True); s.pending_approval=False; s.approved=True
        _step(s,"execute"); _step(s,"finish"); _finish(s,"approved_and_done")
    elif name == "side_effect":
        _step(s,"prepare"); s.effect("mock_payment"); _step(s,"payment"); _step(s,"verify"); _step(s,"finish"); _finish(s,"done")
    return s


def _step(s: RuntimeState, name: str) -> None:
    s.emit("step_started", name)
    s.complete(name)


def _finish(s: RuntimeState, outcome: str) -> None:
    s.terminated = True
    s.outcome = outcome
    s.emit("workflow_terminated", "END", outcome=outcome)
