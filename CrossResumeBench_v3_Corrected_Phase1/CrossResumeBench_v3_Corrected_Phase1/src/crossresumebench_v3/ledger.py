from __future__ import annotations
import json
from pathlib import Path

class FileLedger:
    def __init__(self,path:Path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def read(self):
        if not self.path.exists(): return {"effect_count":0,"ack_count":0,"finish_count":0}
        return json.loads(self.path.read_text(encoding="utf-8"))
    def _write(self,d): self.path.write_text(json.dumps(d,sort_keys=True),encoding="utf-8")
    def commit_effect(self):
        d=self.read(); d["effect_count"]+=1; self._write(d); return d["effect_count"]
    def ack(self):
        d=self.read(); d["ack_count"]+=1; self._write(d)
    def finish(self):
        d=self.read(); d["finish_count"]+=1; self._write(d)
