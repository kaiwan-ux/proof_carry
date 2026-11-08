from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from ..ledger import FileLedger
from ..models import NativePause


class CrewAIRuntime:
    """CrewAI native checkpoint adapter for Revision C.

    Key correction vs Revision A:
    - flow events are NOT suppressed (checkpointing is event-driven)
    - the source Flow runs in a separate process
    - the downstream ack listener blocks on an external gate instead of raising
      before the checkpoint event has time to persist
    - the parent waits for an actual JsonProvider checkpoint file before stopping
      the source process
    """

    name = "crewai"

    def capability_probe(self):
        import crewai
        from crewai import CheckpointConfig
        from crewai.flow.flow import Flow
        from crewai.state import JsonProvider

        return {
            "framework": self.name,
            "installed": True,
            "version": getattr(crewai, "__version__", "unknown"),
            "flow_from_checkpoint": hasattr(Flow, "from_checkpoint"),
            "checkpoint_config": CheckpointConfig is not None,
            "json_provider": JsonProvider is not None,
            "ready": bool(hasattr(Flow, "from_checkpoint") and CheckpointConfig is not None and JsonProvider is not None),
            "pause_kind": "method_execution_finished_checkpoint + external_gate",
        }

    @staticmethod
    def _checkpoints(cpdir: Path) -> list[Path]:
        cpdir = Path(cpdir)
        files = [p for p in cpdir.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".checkpoint"}]
        return sorted(files, key=lambda p: (p.stat().st_mtime_ns, str(p)))

    def _launch_source_worker(self, run_dir: Path, world: str) -> subprocess.Popen:
        root = Path(__file__).resolve().parents[3]
        cfg = {
            "run_dir": str(run_dir),
            "world": world,
            "checkpoint_dir": str(run_dir / "checkpoints"),
            "ledger_path": str(run_dir / "ledger.json"),
            "resume_gate": str(run_dir / "resume.gate"),
            "stop_gate": str(run_dir / "stop.gate"),
            "attempted_signal": str(run_dir / "effect_attempted.signal"),
        }
        cfg_path = run_dir / "crewai_worker_config.json"
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        env = os.environ.copy()
        env.setdefault("CREWAI_TRACING_ENABLED", "false")
        env.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
        env.setdefault("CREWAI_DISABLE_TRACKING", "true")
        env.setdefault("OTEL_SDK_DISABLED", "true")
        cmd = [sys.executable, str(root / "scripts" / "crewai_source_worker.py"), str(cfg_path)]
        return subprocess.Popen(
            cmd,
            cwd=str(root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def capture_effect_pause(self, run_dir, world):
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        cpdir = run_dir / "checkpoints"
        cpdir.mkdir(parents=True, exist_ok=True)
        ledger = run_dir / "ledger.json"
        attempted_signal = run_dir / "effect_attempted.signal"
        stop_gate = run_dir / "stop.gate"

        proc = self._launch_source_worker(run_dir, world)
        deadline = time.time() + 30.0
        checkpoint_files: list[Path] = []
        try:
            while time.time() < deadline:
                if proc.poll() is not None:
                    stdout, stderr = proc.communicate(timeout=2)
                    raise RuntimeError(
                        "CrewAI source worker exited before a checkpoint was captured\n"
                        f"returncode={proc.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                    )
                if attempted_signal.exists():
                    checkpoint_files = self._checkpoints(cpdir)
                    if checkpoint_files:
                        break
                time.sleep(0.05)
            if not attempted_signal.exists():
                raise RuntimeError("CrewAI effect method did not reach the attempted boundary")
            if not checkpoint_files:
                raise RuntimeError(
                    "CrewAI produced no persisted checkpoint after method_execution_finished. "
                    "Revision C leaves Flow events enabled and waits in a downstream gate, so this "
                    "indicates an actual checkpoint capability/runtime issue rather than the Revision A pause race."
                )

            d = FileLedger(ledger).read()
            expected = 1 if world == "committed" else 0
            if d != {"effect_count": expected, "ack_count": 0, "finish_count": 0}:
                raise RuntimeError(f"CrewAI source crossed the ack boundary before capture: {d}")

            chosen = checkpoint_files[-1]
            stop_gate.write_text("stop", encoding="utf-8")
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                stdout, stderr = proc.communicate(timeout=5)
            (run_dir / "crewai_worker_stdout.txt").write_text(stdout or "", encoding="utf-8")
            (run_dir / "crewai_worker_stderr.txt").write_text(stderr or "", encoding="utf-8")

            return NativePause(
                self.name,
                "effect_commit_two_worlds",
                str(chosen),
                "crewai_flow_checkpoint",
                ["ack"],
                {"phase": "effect_attempted"},
                {
                    "framework": self.name,
                    "checkpoint_file": str(chosen),
                    "checkpoint_count": len(checkpoint_files),
                    "worker_returncode": proc.returncode,
                    "events_suppressed": False,
                    "pause_protocol": "subprocess_external_gate",
                },
                d,
                world,
            )
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()

    @staticmethod
    def _flow_class_for_restore():
        from crewai.flow.flow import Flow, listen, start
        from pydantic import BaseModel

        class St(BaseModel):
            ledger_path: str = ""
            world: str = "committed"
            resume_gate: str = ""
            stop_gate: str = ""
            attempted_signal: str = ""
            phase: str = "start"

        class F(Flow[St]):
            @start()
            def effect_attempt(self):
                # If native restore replays this completed method, the external ledger exposes it.
                if self.state.world == "committed":
                    FileLedger(Path(self.state.ledger_path)).commit_effect()
                Path(self.state.attempted_signal).write_text("attempted", encoding="utf-8")
                self.state.phase = "effect_attempted"
                return "attempted"

            @listen(effect_attempt)
            def ack(self, _=None):
                if not Path(self.state.resume_gate).exists():
                    raise RuntimeError("resume gate missing during restored CrewAI run")
                FileLedger(Path(self.state.ledger_path)).ack()
                self.state.phase = "acked"
                return "acked"

            @listen(ack)
            def finish(self, _=None):
                FileLedger(Path(self.state.ledger_path)).finish()
                self.state.phase = "finished"
                return "finished"

        return F

    def self_resume_committed(self, run_dir):
        from crewai import CheckpointConfig

        run_dir = Path(run_dir)
        pause = self.capture_effect_pause(run_dir, "committed")
        (run_dir / "resume.gate").write_text("resume", encoding="utf-8")
        F = self._flow_class_for_restore()
        restored = F.from_checkpoint(CheckpointConfig(restore_from=pause.checkpoint_ref))
        restored.kickoff()
        d = FileLedger(run_dir / "ledger.json").read()
        safe = d == {"effect_count": 1, "ack_count": 1, "finish_count": 1}
        return {
            "restore_completed": True,
            "safe": safe,
            "unsafe_native_replay": not safe,
            "ledger": d,
            "pause": pause.to_dict(),
            "note": "Unsafe native replay is a baseline result, not a technical failure.",
        }

    def run_from_effect_decision(self, effect_status, run_dir):
        from crewai.flow.flow import Flow, listen, start
        from pydantic import BaseModel

        ledger = Path(run_dir) / "ledger.json"
        trace: list[str] = []

        class St(BaseModel):
            ledger_path: str = ""
            effect_status: str = ""
            phase: str = "resume"

        class T(Flow[St]):
            @start()
            def effect_guard(self):
                if self.state.effect_status == "not_committed":
                    FileLedger(Path(self.state.ledger_path)).commit_effect()
                    trace.append("execute_effect")
                elif self.state.effect_status == "committed":
                    trace.append("skip_effect")
                else:
                    raise RuntimeError(f"missing effect decision: {self.state.effect_status!r}")
                self.state.phase = "effect_resolved"
                return "resolved"

            @listen(effect_guard)
            def ack(self, _=None):
                FileLedger(Path(self.state.ledger_path)).ack()
                trace.append("ack")
                self.state.phase = "acked"
                return "acked"

            @listen(ack)
            def finish(self, _=None):
                FileLedger(Path(self.state.ledger_path)).finish()
                trace.append("finish")
                self.state.phase = "finished"
                return "finished"

        t = T()
        t.state.ledger_path = str(ledger)
        t.state.effect_status = effect_status
        out = t.kickoff()
        return {
            "ledger": FileLedger(ledger).read(),
            "effect_decision": trace[0] if trace else "",
            "trace": trace,
            "native_kind": "crewai_target_flow",
            "flow_id": str(t.state.id),
            "result": str(out),
        }
