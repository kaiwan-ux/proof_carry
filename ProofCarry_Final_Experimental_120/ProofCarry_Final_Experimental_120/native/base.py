from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
@dataclass
class NativeProbe:
    runtime: str
    available: bool
    version: str
    self_resume_tested: bool
    source_capture_tested: bool
    expanded_native_tested: bool
    status: str
    detail: str
    def to_dict(self): return asdict(self)
