from __future__ import annotations

import asyncio
import json
from pathlib import Path

from ..ledger import FileLedger
from ..models import NativePause


class MAFRuntime:
    """Microsoft Agent Framework runtime adapter for Phase 1 Revision C.

    Revision C changes only MAF adapter engineering. It intentionally uses explicit
    @handler(input=..., output=...) declarations so the framework does not have to
    introspect locally-scoped/postponed WorkflowContext generic annotations.
    """

    name = "maf"

    def capability_probe(self):
        import agent_framework
        from agent_framework import FileCheckpointStorage, WorkflowBuilder, handler

        return {
            "framework": self.name,
            "installed": True,
            "version": getattr(agent_framework, "__version__", "unknown"),
            "workflow_builder": WorkflowBuilder is not None,
            "file_checkpoint_storage": FileCheckpointStorage is not None,
            "explicit_handler_decorator": handler is not None,
            "ready": bool(WorkflowBuilder is not None and FileCheckpointStorage is not None and handler is not None),
            "pause_kind": "superstep_completed_file_checkpoint",
            "revision_c_maf_fix": "explicit_handler_types_no_context_annotation_introspection",
        }

    @staticmethod
    def _decode(message: str) -> dict:
        return json.loads(message)

    @staticmethod
    def _encode(message: dict) -> str:
        return json.dumps(message, sort_keys=True, separators=(",", ":"))

    def _build_source(self, storage, workflow_name):
        from agent_framework import Executor, WorkflowBuilder, handler

        outer = self

        class Attempt(Executor):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.called = False

            @handler(input=str, output=str)
            async def process(self, message, ctx):
                self.called = True
                data = outer._decode(message)
                if data["world"] == "committed":
                    FileLedger(Path(data["ledger_path"])).commit_effect()
                data["phase"] = "effect_attempted"
                await ctx.send_message(outer._encode(data))

        class Ack(Executor):
            @handler(input=str, output=str)
            async def process(self, message, ctx):
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).ack()
                data["phase"] = "acked"
                await ctx.send_message(outer._encode(data))

        class End(Executor):
            @handler(input=str, workflow_output=str)
            async def process(self, message, ctx):
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).finish()
                data["phase"] = "finished"
                await ctx.yield_output(outer._encode(data))

        attempt = Attempt(id="effect_attempt")
        ack = Ack(id="ack")
        end = End(id="finish")
        builder = WorkflowBuilder(name=workflow_name, start_executor=attempt, checkpoint_storage=storage)
        builder.add_edge(attempt, ack)
        builder.add_edge(ack, end)
        return builder.build(), attempt

    async def _capture_with_context(self, run_dir, world):
        from agent_framework import FileCheckpointStorage

        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        ledger = run_dir / "ledger.json"
        cpdir = run_dir / "checkpoints"
        storage = FileCheckpointStorage(str(cpdir))
        workflow_name = f"crb3-revc-maf-{run_dir.name}"
        workflow, attempt = self._build_source(storage, workflow_name)
        initial = self._encode({"ledger_path": str(ledger), "world": world, "phase": "start"})

        # Microsoft Agent Framework documents superstep_completed as a safe
        # interruption boundary: the current superstep has finished and its
        # checkpoint has been persisted. Stop immediately at that boundary.
        stopped = False
        event_trace = []
        async for event in workflow.run(initial, stream=True):
            etype = getattr(event, "type", None)
            cname = event.__class__.__name__
            event_trace.append({"type": str(etype), "class": cname})
            if attempt.called and (etype == "superstep_completed" or cname == "SuperStepCompletedEvent"):
                stopped = True
                break
        if not stopped:
            raise RuntimeError(
                "MAF did not expose superstep_completed after effect_attempt; "
                f"events={event_trace!r}"
            )

        # Use the documented latest-checkpoint API rather than guessing file order.
        latest = await storage.get_latest(workflow_name=workflow.name)
        if latest is None:
            raise RuntimeError("MAF checkpoint storage is empty after effect_attempt superstep")
        checkpoints = await storage.list_checkpoints(workflow_name=workflow.name)

        observed = FileLedger(ledger).read()
        expected_effect = 1 if world == "committed" else 0
        expected_ledger = {"effect_count": expected_effect, "ack_count": 0, "finish_count": 0}
        if observed != expected_ledger:
            raise RuntimeError(
                "MAF source crossed the ack boundary before capture or lost effect state: "
                f"expected={expected_ledger}, observed={observed}"
            )

        pause = NativePause(
            self.name,
            "effect_commit_two_worlds",
            str(latest.checkpoint_id),
            "maf_superstep_file_checkpoint",
            ["ack"],
            {"phase": "effect_attempted"},
            {
                "framework": self.name,
                "workflow_name": workflow.name,
                "checkpoint_id": str(latest.checkpoint_id),
                "iteration_count": getattr(latest, "iteration_count", None),
                "checkpoint_count": len(checkpoints),
                "storage_path": str(cpdir),
                "event_trace": event_trace,
                "handler_typing_mode": "explicit",
            },
            observed,
            world,
        )
        return pause, cpdir, workflow.name, latest.checkpoint_id, ledger

    def capture_effect_pause(self, run_dir, world):
        pause, *_ = asyncio.run(self._capture_with_context(run_dir, world))
        return pause

    async def _self_resume_async(self, run_dir):
        from agent_framework import FileCheckpointStorage

        pause, cpdir, workflow_name, checkpoint_id, ledger = await self._capture_with_context(run_dir, "committed")
        storage = FileCheckpointStorage(str(cpdir))
        workflow, _ = self._build_source(storage, workflow_name)

        output_seen = False
        async for event in workflow.run(
            checkpoint_id=checkpoint_id,
            checkpoint_storage=storage,
            stream=True,
        ):
            if getattr(event, "type", None) == "output" or event.__class__.__name__ == "WorkflowOutputEvent":
                output_seen = True

        observed = FileLedger(ledger).read()
        safe_ledger = {"effect_count": 1, "ack_count": 1, "finish_count": 1}
        return {
            "restore_completed": True,
            "safe": observed == safe_ledger,
            "unsafe_native_replay": observed != safe_ledger,
            "ledger": observed,
            "output_seen": output_seen,
            "pause": pause.to_dict(),
        }

    def self_resume_committed(self, run_dir):
        return asyncio.run(self._self_resume_async(run_dir))

    async def _target_async(self, effect_status, run_dir):
        from agent_framework import Executor, WorkflowBuilder, handler

        outer = self
        ledger = Path(run_dir) / "ledger.json"
        trace: list[str] = []

        class Guard(Executor):
            @handler(input=str, output=str)
            async def process(self, message, ctx):
                data = outer._decode(message)
                status = data["effect_status"]
                if status == "not_committed":
                    FileLedger(Path(data["ledger_path"])).commit_effect()
                    trace.append("execute_effect")
                elif status == "committed":
                    trace.append("skip_effect")
                else:
                    raise RuntimeError(f"missing effect decision: {status!r}")
                data["phase"] = "effect_resolved"
                await ctx.send_message(outer._encode(data))

        class Ack(Executor):
            @handler(input=str, output=str)
            async def process(self, message, ctx):
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).ack()
                trace.append("ack")
                data["phase"] = "acked"
                await ctx.send_message(outer._encode(data))

        class End(Executor):
            @handler(input=str, workflow_output=str)
            async def process(self, message, ctx):
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).finish()
                trace.append("finish")
                data["phase"] = "finished"
                await ctx.yield_output(outer._encode(data))

        guard = Guard(id="effect_guard")
        ack = Ack(id="ack")
        end = End(id="finish")
        builder = WorkflowBuilder(name=f"crb3-revc-target-{Path(run_dir).name}", start_executor=guard)
        builder.add_edge(guard, ack)
        builder.add_edge(ack, end)
        workflow = builder.build()

        output = None
        initial = outer._encode({"ledger_path": str(ledger), "effect_status": effect_status, "phase": "resume"})
        async for event in workflow.run(initial, stream=True):
            if getattr(event, "type", None) == "output" or event.__class__.__name__ == "WorkflowOutputEvent":
                output = getattr(event, "data", None)

        return {
            "ledger": FileLedger(ledger).read(),
            "effect_decision": trace[0] if trace else "",
            "trace": trace,
            "native_kind": "maf_target_workflow_explicit_handlers",
            "result": output,
        }

    def run_from_effect_decision(self, effect_status, run_dir):
        return asyncio.run(self._target_async(effect_status, run_dir))
