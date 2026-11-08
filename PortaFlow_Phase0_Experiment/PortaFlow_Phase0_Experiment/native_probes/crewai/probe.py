from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path


def main() -> None:
    from pydantic import BaseModel, Field
    from crewai.flow.flow import Flow, listen, start
    from crewai.flow.persistence import persist
    from crewai.flow.persistence.sqlite import SQLiteFlowPersistence

    tmp=Path(tempfile.mkdtemp(prefix="portaflow-crewai-"))
    db=tmp/"flows.db"
    persistence=SQLiteFlowPersistence(str(db))

    class S(BaseModel):
        id: str = ""
        completed: list[str] = Field(default_factory=list)
        counter: int = 0

    @persist(persistence)
    class F(Flow[S]):
        @start()
        def a(self):
            self.state.completed.append("A"); self.state.counter += 1; return "A"

        @listen(a)
        def b(self, _):
            self.state.completed.append("B"); self.state.counter += 1; return "B"

        @listen(b)
        def c(self, _):
            self.state.completed.append("C"); self.state.counter += 1; return "C"

    f1=F(persistence=persistence)
    out1=f1.kickoff()
    sid=f1.state.id

    rows=[]
    con=sqlite3.connect(db)
    try:
        tables=[r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
        if "flow_states" in tables:
            cols=[r[1] for r in con.execute("pragma table_info(flow_states)")]
            for row in con.execute("select * from flow_states order by rowid"):
                d=dict(zip(cols,row))
                if "state_json" in d:
                    try: d["state_json_parsed"]=json.loads(d["state_json"])
                    except Exception: pass
                rows.append(d)
    finally:
        con.close()

    f2=F(persistence=persistence)
    out2=f2.kickoff(inputs={"id":sid})

    payload={
        "framework":"crewai",
        "status":"ok",
        "probe":"flow_persistence",
        "db_tables":tables,
        "snapshot_rows":rows,
        "first":{"id":sid,"output":str(out1),"state":f1.state.model_dump()},
        "resume_latest":{"output":str(out2),"state":f2.state.model_dump()},
        "note":"CrewAI @persist snapshots state after flow methods; this probe preserves every persisted row for inspection."
    }
    print(json.dumps(payload, default=str))

if __name__=="__main__":
    main()
