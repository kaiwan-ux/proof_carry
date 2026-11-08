from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "frozen_v2" / "src")]

from crossresumebench_crewai_gate.ledger import FileLedger


class SourceStop(RuntimeError):
    pass


def main(cfg_path: str) -> None:
    from crewai import CheckpointConfig
    from crewai.flow.flow import Flow, listen, start
    from crewai.state import JsonProvider
    from pydantic import BaseModel

    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))

    class St(BaseModel):
        ledger_path: str = ""
        world: str = "committed"
        resume_gate: str = ""
        stop_gate: str = ""
        attempted_signal: str = ""
        phase: str = "start"

    class F(Flow[St]):
        # DO NOT set suppress_flow_events=True: CheckpointConfig is event-driven.
        @start()
        def effect_attempt(self):
            if self.state.world == "committed":
                FileLedger(Path(self.state.ledger_path)).commit_effect()
            self.state.phase = "effect_attempted"
            Path(self.state.attempted_signal).write_text("attempted", encoding="utf-8")
            return "attempted"

        @listen(effect_attempt)
        def ack(self, _=None):
            # Keep the source genuinely in-flight while the parent observes the durable checkpoint.
            while True:
                if Path(self.state.resume_gate).exists():
                    FileLedger(Path(self.state.ledger_path)).ack()
                    self.state.phase = "acked"
                    return "acked"
                if Path(self.state.stop_gate).exists():
                    raise SourceStop("REVISION_B_CAPTURED_CHECKPOINT_STOP")
                time.sleep(0.05)

        @listen(ack)
        def finish(self, _=None):
            FileLedger(Path(self.state.ledger_path)).finish()
            self.state.phase = "finished"
            return "finished"

    cp = CheckpointConfig(
        location=cfg["checkpoint_dir"],
        on_events=["method_execution_finished"],
        provider=JsonProvider(),
        max_checkpoints=20,
    )
    flow = F(checkpoint=cp)
    flow.state.ledger_path = cfg["ledger_path"]
    flow.state.world = cfg["world"]
    flow.state.resume_gate = cfg["resume_gate"]
    flow.state.stop_gate = cfg["stop_gate"]
    flow.state.attempted_signal = cfg["attempted_signal"]

    try:
        flow.kickoff()
    except SourceStop:
        return


if __name__ == "__main__":
    main(sys.argv[1])
