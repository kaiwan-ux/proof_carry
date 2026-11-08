from __future__ import annotations
from typing import Any
import tempfile,sqlite3,json
from pathlib import Path
from ..models import ExecutionState,SourceCapture
from ..benchmark import initial_state,source_prefix_transition,continuation_transition

def _rows(db:Path):
    if not db.exists(): return []
    con=sqlite3.connect(db); out=[]
    try:
        if "flow_states" not in [r[0] for r in con.execute("select name from sqlite_master where type='table'")]: return []
        cols=[r[1] for r in con.execute("pragma table_info(flow_states)")]
        for row in con.execute("select * from flow_states order by rowid"):
            d=dict(zip(cols,row));
            if "state_json" in d:
                try:d["state_json_parsed"]=json.loads(d["state_json"])
                except Exception: pass
            out.append(d)
    finally: con.close()
    return out

def run_source(workflow:str)->SourceCapture:
    from pydantic import BaseModel,Field
    from crewai.flow.flow import Flow,start
    from crewai.flow.persistence import persist
    from crewai.flow.persistence.sqlite import SQLiteFlowPersistence
    tmp=Path(tempfile.mkdtemp(prefix="min-crewai-src-")); db=tmp/"flow.db"; persistence=SQLiteFlowPersistence(str(db))
    class S(BaseModel): id:str=""; logical:dict[str,Any]=Field(default_factory=dict); ledger:dict[str,int]=Field(default_factory=dict)
    @persist(persistence)
    class F(Flow[S]):
        @start()
        def prefix(self):
            s=ExecutionState.from_dict(self.state.logical); ld=dict(self.state.ledger); out=source_prefix_transition(s,ld); self.state.logical=out.to_dict(); self.state.ledger=ld; return self.state.logical
    f=F(persistence=persistence); f.kickoff(inputs={"logical":initial_state(workflow).to_dict(),"ledger":{}})
    return SourceCapture("crewai",workflow,dict(f.state.logical),{"kind":"crewai_flow_persistence","flow_id":str(f.state.id),"state":f.state.model_dump(),"persistence_rows":_rows(db)},dict(f.state.ledger))

def run_target(workflow:str,imported:ExecutionState,ledger:dict[str,int]):
    from pydantic import BaseModel,Field
    from crewai.flow.flow import Flow,start
    class S(BaseModel): id:str=""; logical:dict[str,Any]=Field(default_factory=dict); ledger:dict[str,int]=Field(default_factory=dict)
    class F(Flow[S]):
        @start()
        def cont(self):
            s=ExecutionState.from_dict(self.state.logical); ld=dict(self.state.ledger); out=continuation_transition(s,ld); self.state.logical=out.to_dict(); self.state.ledger=ld; return self.state.logical
    f=F(); f.kickoff(inputs={"logical":imported.to_dict(),"ledger":dict(ledger)}); ledger.clear(); ledger.update(f.state.ledger)
    return ExecutionState.from_dict(f.state.logical),{"kind":"crewai_flow_state","flow_id":str(f.state.id),"state":f.state.model_dump()}
