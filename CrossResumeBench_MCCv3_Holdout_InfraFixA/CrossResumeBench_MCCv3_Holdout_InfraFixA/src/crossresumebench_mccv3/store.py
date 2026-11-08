from __future__ import annotations
import json, copy
from pathlib import Path

EMPTY={"effects":{},"units":{},"approvals":{},"callbacks":{},"compensations":{},"counters":{},"decisions":{},"finish_count":0,"trace":[]}

class SemanticStore:
    def __init__(self,path): self.path=Path(path)
    def read(self):
        if not self.path.exists(): return copy.deepcopy(EMPTY)
        d=json.loads(self.path.read_text(encoding="utf-8"))
        base=copy.deepcopy(EMPTY); base.update(d); return base
    def write(self,d):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(d,indent=2,sort_keys=True),encoding="utf-8")
    def update(self,fn):
        d=self.read(); fn(d); self.write(d); return d
    def apply(self,action):
        a=dict(action); kind=a["kind"]
        def f(d):
            if kind=="effect":
                op=a["operation"]; d["effects"][op]=int(d["effects"].get(op,0))+1
                if a.get("unit"): d["units"][a["unit"]]=int(d["units"].get(a["unit"],0))+1
            elif kind=="unit":
                u=a["unit"]; d["units"][u]=int(d["units"].get(u,0))+1
            elif kind=="approval":
                rid=a["id"]; d["approvals"][rid]=int(d["approvals"].get(rid,0))+1
                if a.get("unit"): d["units"][a["unit"]]=int(d["units"].get(a["unit"],0))+1
            elif kind=="callback":
                cid=a["id"]; d["callbacks"][cid]=int(d["callbacks"].get(cid,0))+1
                if a.get("unit"): d["units"][a["unit"]]=int(d["units"].get(a["unit"],0))+1
            elif kind=="compensation":
                ca=a["action"]; d["compensations"][ca]=int(d["compensations"].get(ca,0))+1
                if a.get("unit"): d["units"][a["unit"]]=int(d["units"].get(a["unit"],0))+1
            elif kind=="counter": d["counters"][a["key"]]=int(a["value"])
            elif kind=="decision": d["decisions"][a["key"]]=a["value"]
            elif kind=="finish": d["finish_count"]=int(d.get("finish_count",0))+1
            else: raise KeyError(kind)
            d["trace"].append(a)
        return self.update(f)

def clone_store(src,dst):
    d=SemanticStore(src).read(); SemanticStore(dst).write(d); return d
