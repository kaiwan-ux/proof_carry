from __future__ import annotations
from typing import Protocol
from ..models import RuntimeState
class Adapter(Protocol):
    name:str
    def run_target(self,family:str,state:RuntimeState,ledger:dict[str,int]): ...
