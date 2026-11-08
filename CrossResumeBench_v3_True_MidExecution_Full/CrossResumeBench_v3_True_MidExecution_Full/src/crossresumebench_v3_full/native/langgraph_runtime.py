from __future__ import annotations
from pathlib import Path
from typing import TypedDict
from ..models import NativePause
from ..semantics import apply_source_pause,apply_plan,oracle_plan,expected_final
from ..store import SemanticStore

class S(TypedDict,total=False):
    store_path:str; case_id:str; phase:str

class LangGraphRuntime:
    name="langgraph"
    def capability_probe(self):
        import langgraph
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.graph import StateGraph
        return {"framework":self.name,"installed":True,"version":getattr(langgraph,"__version__","unknown"),"ready":bool(InMemorySaver and StateGraph),"pause_kind":"checkpoint_interrupt_before_resume"}
    def _source_graph(self,case,cp):
        from langgraph.graph import StateGraph,START,END
        b=StateGraph(S)
        def source(st): apply_source_pause(case,st["store_path"]); return {"phase":"paused"}
        def resume(st): apply_plan(oracle_plan(case),st["store_path"]); return {"phase":"finished"}
        b.add_node("source_boundary",source); b.add_node("resume",resume); b.add_edge(START,"source_boundary"); b.add_edge("source_boundary","resume"); b.add_edge("resume",END)
        return b.compile(checkpointer=cp)
    def capture_case_pause(self,case,run_dir):
        from langgraph.checkpoint.memory import InMemorySaver
        run_dir=Path(run_dir); store=run_dir/"semantic_store.json"; cp=InMemorySaver(); g=self._source_graph(case,cp); cfg={"configurable":{"thread_id":f"full-{case.case_id}-{run_dir.name}"}}
        g.invoke({"store_path":str(store),"case_id":case.case_id,"phase":"start"},config=cfg,interrupt_before=["resume"])
        snap=g.get_state(cfg)
        if list(snap.next)!=["resume"]: raise RuntimeError(f"LangGraph pause mismatch {snap.next}")
        self._live=(g,cfg,store)
        return NativePause(self.name,case.case_id,f"thread:{cfg['configurable']['thread_id']}","langgraph_checkpoint",list(snap.next),{"phase":"mid_execution"},{"framework":self.name,"next":list(snap.next),"values_keys":sorted(dict(snap.values).keys()),"config":dict(snap.config)},SemanticStore(store).read())
    def self_resume_case(self,case,run_dir):
        p=self.capture_case_pause(case,run_dir); g,cfg,store=self._live; g.invoke(None,config=cfg); d=SemanticStore(store).read(); exp=expected_final(case)
        return {"restore_completed":True,"safe":_eq(exp,d),"store":d,"pause":p.to_dict()}
    def run_plan(self,case,plan,run_dir):
        from langgraph.graph import StateGraph,START,END
        run_dir=Path(run_dir); store=run_dir/"semantic_store.json"; trace=[]
        class T(TypedDict,total=False): store_path:str; phase:str
        b=StateGraph(T)
        def execute(st): apply_plan(plan,st["store_path"]); trace.extend(plan); return {"phase":"finished"}
        b.add_node("resume_plan",execute); b.add_edge(START,"resume_plan"); b.add_edge("resume_plan",END)
        out=b.compile().invoke({"store_path":str(store),"phase":"resume"})
        return {"store":SemanticStore(store).read(),"trace":trace,"native_kind":"langgraph_target_graph","final":out}

def _eq(a,b):
    a=dict(a); b=dict(b); a.pop("trace",None); b.pop("trace",None); return a==b
