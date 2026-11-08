from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing_extensions import Never

from ..ledger import FileLedger
from ..models import NativePause


class MAFRuntime:
    name = "maf"

    def capability_probe(self):
        import agent_framework
        from agent_framework import FileCheckpointStorage, WorkflowBuilder

        return {
            "framework": self.name,
            "installed": True,
            "version": getattr(agent_framework, "__version__", "unknown"),
            "workflow_builder": WorkflowBuilder is not None,
            "file_checkpoint_storage": FileCheckpointStorage is not None,
            "ready": bool(WorkflowBuilder is not None and FileCheckpointStorage is not None),
            "pause_kind": "superstep_completed_file_checkpoint",
        }

    @staticmethod
    def _decode(message: str) -> dict:
        return json.loads(message)

    @staticmethod
    def _encode(message: dict) -> str:
        return json.dumps(message, sort_keys=True, separators=(",", ":"))

    def _build_source(self, storage, workflow_name):
        from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

        outer = self

        class Attempt(Executor):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.called = False

            @handler
            async def process(self, message: str, ctx: WorkflowContext[str]) -> None:
                self.called = True
                data = outer._decode(message)
                if data["world"] == "committed":
                    FileLedger(Path(data["ledger_path"])).commit_effect()
                data["phase"] = "effect_attempted"
                await ctx.send_message(outer._encode(data))

        class Ack(Executor):
            @handler
            async def process(self, message: str, ctx: WorkflowContext[str]) -> None:
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).ack()
                data["phase"] = "acked"
                await ctx.send_message(outer._encode(data))

        class End(Executor):
            @handler
            async def process(self, message: str, ctx: WorkflowContext[Never, str]) -> None:
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).finish()
                data["phase"] = "finished"
                await ctx.yield_output(outer._encode(data))

        attempt = Attempt(id="effect_attempt")
        ack = Ack(id="ack")
        end = End(id="finish")
        wb = WorkflowBuilder(name=workflow_name, start_executor=attempt, checkpoint_storage=storage)
        wb.add_edge(attempt, ack)
        wb.add_edge(ack, end)
        return wb.build(), attempt

    async def _capture_with_context(self, run_dir, world):
        from agent_framework import FileCheckpointStorage

        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        ledger = run_dir / "ledger.json"
        cpdir = run_dir / "checkpoints"
        storage = FileCheckpointStorage(str(cpdir))
        workflow_name = f"crb3-revb-maf-{run_dir.name}"
        wf, attempt = self._build_source(storage, workflow_name)
        initial = self._encode({"ledger_path": str(ledger), "world": world, "phase": "start"})

        stopped = False
        async for event in wf.run(initial, stream=True):
            etype = getattr(event, "type", None)
            cname = event.__class__.__name__
            if attempt.called and (etype == "superstep_completed" or cname == "SuperStepCompletedEvent"):
                stopped = True
                break
        if not stopped:
            raise RuntimeError("MAF did not expose a superstep_completed event after the effect attempt")

        checkpoints = await storage.list_checkpoints(workflow_name=wf.name)
        if not checkpoints:
            raise RuntimeError("MAF checkpoint storage is empty after effect-attempt superstep")
        latest = max(checkpoints, key=lambda c: (getattr(c, "iteration_count", -1), str(c.checkpoint_id)))

        d = FileLedger(ledger).read()
        expected = 1 if world == "committed" else 0
        if d != {"effect_count": expected, "ack_count": 0, "finish_count": 0}:
            raise RuntimeError(f"MAF source crossed the ack boundary before capture: {d}")

        pause = NativePause(
            self.name,
            "effect_commit_two_worlds",
            str(latest.checkpoint_id),
            "maf_superstep_file_checkpoint",
            ["ack"],
            {"phase": "effect_attempted"},
            {
                "framework": self.name,
                "workflow_name": wf.name,
                "checkpoint_id": str(latest.checkpoint_id),
                "iteration_count": getattr(latest, "iteration_count", None),
                "checkpoint_count": len(checkpoints),
                "storage_path": str(cpdir),
            },
            d,
            world,
        )
        return pause, cpdir, wf.name, latest.checkpoint_id, ledger

    def capture_effect_pause(self, run_dir, world):
        pause, *_ = asyncio.run(self._capture_with_context(run_dir, world))
        return pause

    async def _self_resume_async(self, run_dir):
        from agent_framework import FileCheckpointStorage

        pause, cpdir, workflow_name, checkpoint_id, ledger = await self._capture_with_context(run_dir, "committed")
        storage = FileCheckpointStorage(str(cpdir))
        wf, _ = self._build_source(storage, workflow_name)
        async for _ in wf.run(checkpoint_id=checkpoint_id, checkpoint_storage=storage, stream=True):
            pass
        d = FileLedger(ledger).read()
        return {
            "restore_completed": True,
            "safe": d == {"effect_count": 1, "ack_count": 1, "finish_count": 1},
            "unsafe_native_replay": d != {"effect_count": 1, "ack_count": 1, "finish_count": 1},
            "ledger": d,
            "pause": pause.to_dict(),
        }

    def self_resume_committed(self, run_dir):
        return asyncio.run(self._self_resume_async(run_dir))

    async def _target_async(self, effect_status, run_dir):
        from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

        outer = self
        ledger = Path(run_dir) / "ledger.json"
        trace: list[str] = []

        class Guard(Executor):
            @handler
            async def process(self, message: str, ctx: WorkflowContext[str]) -> None:
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
            @handler
            async def process(self, message: str, ctx: WorkflowContext[str]) -> None:
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).ack()
                trace.append("ack")
                data["phase"] = "acked"
                await ctx.send_message(outer._encode(data))

        class End(Executor):
            @handler
            async def process(self, message: str, ctx: WorkflowContext[Never, str]) -> None:
                data = outer._decode(message)
                FileLedger(Path(data["ledger_path"])).finish()
                trace.append("finish")
                data["phase"] = "finished"
                await ctx.yield_output(outer._encode(data))

        guard = Guard(id="effect_guard")
        ack = Ack(id="ack")
        end = End(id="finish")
        wf = WorkflowBuilder(name=f"crb3-revb-target-{Path(run_dir).name}", start_executor=guard).add_edge(guard, ack).add_edge(ack, end).build()
        output = None
        initial = outer._encode({"ledger_path": str(ledger), "effect_status": effect_status, "phase": "resume"})
        async for event in wf.run(initial, stream=True):
            if getattr(event, "type", None) == "output" or event.__class__.__name__ == "WorkflowOutputEvent":
                output = getattr(event, "data", None)
        return {
            "ledger": FileLedger(ledger).read(),
            "effect_decision": trace[0] if trace else "",
            "trace": trace,
            "native_kind": "maf_target_workflow",
            "result": output,
        }

    def run_from_effect_decision(self, effect_status, run_dir):
        return asyncio.run(self._target_async(effect_status, run_dir))
