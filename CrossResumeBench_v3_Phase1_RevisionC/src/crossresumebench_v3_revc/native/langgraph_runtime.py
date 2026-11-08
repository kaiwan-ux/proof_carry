from __future__ import annotations
from pathlib import Path
from typing import TypedDict
from ..models import NativePause
from ..ledger import FileLedger

class S(TypedDict,total=False):
    ledger_path:str
    world:str
    phase:str
    effect_status:str

class LangGraphRuntime:
    name="langgraph"
    def capability_probe(self):
        import langgraph
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.graph import StateGraph
        return {"framework":self.name,"installed":True,"ready":bool(InMemorySaver is not None and StateGraph is not None),"version":getattr(langgraph,"__version__","unknown"),"pause_kind":"interrupt_before_ack","checkpointer":InMemorySaver is not None,"stategraph":StateGraph is not None}
    def _source_graph(self,cp):
        from langgraph.graph import StateGraph,START,END
        b=StateGraph(S)
        def attempt(st):
            if st["world"]=="committed": FileLedger(st["ledger_path"]).commit_effect()
            return {"phase":"effect_attempted"}
        def ack(st): FileLedger(st["ledger_path"]).ack(); return {"phase":"acked"}
        def finish(st): FileLedger(st["ledger_path"]).finish(); return {"phase":"finished"}
        b.add_node("effect_attempt",attempt); b.add_node("ack",ack); b.add_node("finish",finish)
        b.add_edge(START,"effect_attempt"); b.add_edge("effect_attempt","ack"); b.add_edge("ack","finish"); b.add_edge("finish",END)
        return b.compile(checkpointer=cp)
    def capture_effect_pause(self,run_dir,world):
        from langgraph.checkpoint.memory import InMemorySaver
        run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; cp=InMemorySaver(); g=self._source_graph(cp)
        cfg={"configurable":{"thread_id":f"revc-lg-{run_dir.name}"}}
        g.invoke({"ledger_path":str(ledger),"world":world,"phase":"start"},config=cfg,interrupt_before=["ack"])
        snap=g.get_state(cfg); d=FileLedger(ledger).read()
        if list(snap.next)!=["ack"]: raise RuntimeError(f"LangGraph did not pause before ack: {snap.next}")
        expected=1 if world=="committed" else 0
        if d!={"effect_count":expected,"ack_count":0,"finish_count":0}: raise RuntimeError(f"bad source ledger: {d}")
        self._live=(g,cfg,ledger)
        return NativePause(self.name,"effect_commit_two_worlds",f"thread:{cfg['configurable']['thread_id']}","langgraph_checkpoint",list(snap.next),{"phase":"effect_attempted"},{"framework":self.name,"next":list(snap.next),"config":dict(snap.config),"values":dict(snap.values)},d,world)
    def self_resume_committed(self,run_dir):
        p=self.capture_effect_pause(run_dir,"committed"); g,cfg,ledger=self._live; g.invoke(None,config=cfg); d=FileLedger(ledger).read()
        return {"restore_completed":True,"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"unsafe_native_replay":d!={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
    def run_from_effect_decision(self,effect_status,run_dir):
        from langgraph.graph import StateGraph,START,END
        b=StateGraph(S); ledger=Path(run_dir)/"ledger.json"; trace=[]
        def guard(st):
            status=st["effect_status"]
            if status=="not_committed": FileLedger(st["ledger_path"]).commit_effect(); trace.append("execute_effect")
            elif status=="committed": trace.append("skip_effect")
            else: raise RuntimeError(f"missing effect decision: {status!r}")
            return {"phase":"effect_resolved"}
        def ack(st): FileLedger(st["ledger_path"]).ack(); trace.append("ack"); return {"phase":"acked"}
        def finish(st): FileLedger(st["ledger_path"]).finish(); trace.append("finish"); return {"phase":"finished"}
        b.add_node("effect_guard",guard); b.add_node("ack",ack); b.add_node("finish",finish)
        b.add_edge(START,"effect_guard"); b.add_edge("effect_guard","ack"); b.add_edge("ack","finish"); b.add_edge("finish",END)
        out=b.compile().invoke({"ledger_path":str(ledger),"effect_status":effect_status,"phase":"resume"})
        return {"ledger":FileLedger(ledger).read(),"effect_decision":trace[0] if trace else "","trace":trace,"native_kind":"langgraph_target_graph","final":out}
