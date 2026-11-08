from __future__ import annotations
import json
from pathlib import Path

EMPTY={"effect_count":0,"ack_count":0,"finish_count":0}

class FileLedger:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def read(self):
        if not self.path.exists(): return dict(EMPTY)
        d=json.loads(self.path.read_text(encoding="utf-8"))
        return {k:int(d.get(k,0)) for k in EMPTY}
    def write(self,d):
        out={k:int(d.get(k,0)) for k in EMPTY}; self.path.write_text(json.dumps(out,sort_keys=True),encoding="utf-8"); return out
    def commit_effect(self):
        d=self.read(); d["effect_count"]+=1; self.write(d); return d["effect_count"]
    def ack(self):
        d=self.read(); d["ack_count"]+=1; self.write(d); return d["ack_count"]
    def finish(self):
        d=self.read(); d["finish_count"]+=1; self.write(d); return d["finish_count"]
