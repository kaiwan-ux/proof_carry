import json,tempfile,sqlite3
from pathlib import Path

def main():
    from pydantic import BaseModel,Field
    from crewai.flow.flow import Flow,start,listen
    from crewai.flow.persistence import persist
    from crewai.flow.persistence.sqlite import SQLiteFlowPersistence
    tmp=Path(tempfile.mkdtemp(prefix="pf-crew-probe-")); db=tmp/"f.db"; persistence=SQLiteFlowPersistence(str(db))
    class S(BaseModel): id:str=""; completed:list[str]=Field(default_factory=list)
    @persist(persistence)
    class F(Flow[S]):
        @start()
        def a(self): self.state.completed.append("A"); return "A"
        @listen(a)
        def b(self,_): self.state.completed.append("B"); return "B"
    f1=F(persistence=persistence); f1.kickoff(); sid=f1.state.id; before=list(f1.state.completed)
    f2=F(persistence=persistence); f2.kickoff(inputs={"id":sid}); after=list(f2.state.completed)
    print(json.dumps({"framework":"crewai","status":"ok","flow_id":sid,"before_reload_kickoff":before,"after_reload_kickoff":after,"reexecuted":len(after)>len(before)},default=str))
if __name__=="__main__": main()
