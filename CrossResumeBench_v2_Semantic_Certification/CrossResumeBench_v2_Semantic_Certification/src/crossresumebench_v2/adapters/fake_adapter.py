from __future__ import annotations
from ..source_engine import simulate_source
from ..target_engine import execute_target
class FakeAdapter:
    def __init__(self,name="fake"): self.name=name
    def capture_source(self,case):
        return simulate_source(case,{"kind":f"{self.name}_fake_source","framework":self.name,"real_native":False})
    def run_target(self,case,continuation,ledger):
        return execute_target(case,continuation,ledger,{"kind":f"{self.name}_fake_target","framework":self.name,"real_native":False})
