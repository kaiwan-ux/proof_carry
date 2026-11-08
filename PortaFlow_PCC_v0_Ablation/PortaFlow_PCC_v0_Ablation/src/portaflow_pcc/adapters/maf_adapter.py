# Intentionally no `from __future__ import annotations`.
# agent-framework-core validates WorkflowContext annotations when handlers are registered.
import asyncio
from typing import Any
from typing_extensions import Never
from ..models import LogicalState, SourceCapture
from ..scenarios import source_prefix_transition, continuation_transition


def _serialise_event(event):
    return {
        "type": getattr(event, "type", type(event).__name__),
        "executor_id": getattr(event, "executor_id", None),
        "data": getattr(event, "data", None),
    }


async def _run(mode: str, logical: dict[str, Any], ledger: dict[str, int]):
    from agent_framework import Executor, InMemoryCheckpointStorage, WorkflowBuilder, WorkflowContext, handler
    try:
        from typing import override
    except ImportError:
        from typing_extensions import override

    class Start(Executor):
        @handler
        async def process(self, message: dict, ctx: WorkflowContext[dict]) -> None:
            await ctx.send_message(message)

    class Work(Executor):
        def __init__(self, id: str):
            super().__init__(id=id)
            self.last_state: dict[str, Any] = {}

        @handler
        async def process(self, message: dict, ctx: WorkflowContext[dict]) -> None:
            s = LogicalState.from_dict(message["logical"])
            ld = dict(message.get("ledger", {}))
            out = source_prefix_transition(s, ld) if mode == "source" else continuation_transition(s, ld)
            self.last_state = {"logical": out.to_dict(), "ledger": ld}
            await ctx.send_message(self.last_state)

        @override
        async def on_checkpoint_save(self) -> dict[str, Any]:
            return {"last_state": self.last_state}

        @override
        async def on_checkpoint_restore(self, state: dict[str, Any]) -> None:
            self.last_state = dict((state or {}).get("last_state", {}))

    class End(Executor):
        @handler
        async def process(self, message: dict, ctx: WorkflowContext[Never, dict]) -> None:
            await ctx.yield_output(message)

    storage = InMemoryCheckpointStorage()
    a = Start(id="start")
    b = Work(id="work")
    c = End(id="end")
    wf = WorkflowBuilder(start_executor=a, checkpoint_storage=storage).add_edge(a, b).add_edge(b, c).build()
    events = []
    output = None
    async for event in wf.run(message={"logical": logical, "ledger": ledger}, stream=True):
        events.append(_serialise_event(event))
        if getattr(event, "type", None) == "output":
            output = event.data
    if output is None:
        raise RuntimeError("MAF workflow produced no output event")
    cps = await storage.list_checkpoints(workflow_name=wf.name)
    latest = await storage.get_latest(workflow_name=wf.name)
    snap = {
        "kind": "maf_workflow_checkpoint",
        "workflow_name": wf.name,
        "checkpoint_count": len(cps),
        "events": events,
        "latest_checkpoint": latest.to_dict() if latest is not None and hasattr(latest, "to_dict") else None,
    }
    return output, snap


def run_source(workflow: str) -> SourceCapture:
    initial = LogicalState(workflow=workflow, request_id=f"pcc-{workflow}-001")
    output, snap = asyncio.run(_run("source", initial.to_dict(), {}))
    return SourceCapture("maf", workflow, dict(output["logical"]), snap, dict(output["ledger"]))


def run_target(workflow: str, imported: LogicalState, ledger: dict[str, int]) -> tuple[LogicalState, dict[str, Any]]:
    output, snap = asyncio.run(_run("target", imported.to_dict(), dict(ledger)))
    ledger.clear(); ledger.update(output["ledger"])
    return LogicalState.from_dict(output["logical"]), snap
