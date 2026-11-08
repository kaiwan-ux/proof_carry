from __future__ import annotations
from pathlib import Path
from typing import TypedDict
from ..models import NativePause
from ..ledger import FileLedger

class S(TypedDict, total=False):
    ledger_path:str
    phase:str

class LangGraphRuntime:
    name="langgraph"
    def capability_probe(self):
        import langgraph
        from langgraph.types import interrupt
        from langgraph.checkpoint.memory import InMemorySaver
        return {"framework":self.name,"installed":True,"version":getattr(langgraph,"__version__","unknown"),"native_checkpoint_api":True,"pause_kind":"static_interrupt_before"}
    def _build(self, cp, ledger_path):
        from langgraph.graph import StateGraph, START, END
        b=StateGraph(S)
        def commit(st): FileLedger(Path(st["ledger_path"])).commit_effect(); return {"phase":"effect_committed"}
        def ack(st): FileLedger(Path(st["ledger_path"])).ack(); return {"phase":"acked"}
        def finish(st): FileLedger(Path(st["ledger_path"])).finish(); return {"phase":"finished"}
        b.add_node("commit_effect",commit); b.add_node("ack",ack); b.add_node("finish",finish)
        b.add_edge(START,"commit_effect"); b.add_edge("commit_effect","ack"); b.add_edge("ack","finish"); b.add_edge("finish",END)
        return b.compile(checkpointer=cp)
    def capture_effect_ack_pause(self,run_dir):
        from langgraph.checkpoint.memory import InMemorySaver
        run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; cp=InMemorySaver(); g=self._build(cp,ledger)
        cfg={"configurable":{"thread_id":f"crb3-lg-{run_dir.name}"}}
        g.invoke({"ledger_path":str(ledger),"phase":"start"},config=cfg,interrupt_before=["ack"])
        snap=g.get_state(cfg)
        if "ack" not in list(snap.next): raise RuntimeError(f"LangGraph pause did not leave ack pending: {snap.next}")
        # Store live objects only in runtime process; checkpoint_ref is a logical handle for artifact provenance.
        self._live=(g,cfg,ledger)
        return NativePause(self.name,"effect_committed_ack_pending",f"thread:{cfg['configurable']['thread_id']}","langgraph_state_snapshot",list(snap.next),{"phase":"effect_committed"},[],[],{"next":list(snap.next),"config":dict(snap.config),"values":dict(snap.values)},FileLedger(ledger).read()["effect_count"])
    def self_resume_effect_ack(self,run_dir):
        p=self.capture_effect_ack_pause(run_dir); g,cfg,ledger=self._live; g.invoke(None,config=cfg); d=FileLedger(ledger).read(); return {"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
    def run_ack_finish_from_mcc(self,reconstructed,run_dir):
        from langgraph.graph import StateGraph,START,END
        run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; l=FileLedger(ledger)
        # Seed the target-side external world with the already committed source effect.
        if l.read()["effect_count"]==0: l.commit_effect()
        b=StateGraph(S)
        def ack(st): FileLedger(Path(st["ledger_path"])).ack(); return {"phase":"acked"}
        def finish(st): FileLedger(Path(st["ledger_path"])).finish(); return {"phase":"finished"}
        b.add_node("ack",ack); b.add_node("finish",finish); b.add_edge(START,"ack"); b.add_edge("ack","finish"); b.add_edge("finish",END)
        out=b.compile().invoke({"ledger_path":str(ledger),"phase":"resume"}); d=l.read(); return {"ledger":d,"native_kind":"langgraph_target_graph","final":out}
