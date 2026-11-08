from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FROZEN_SRC=ROOT/"frozen_v2"/"src"
if str(FROZEN_SRC) not in sys.path: sys.path.insert(0,str(FROZEN_SRC))

from crossresumebench_v2.models import CaseSpec, SourceCapture
from crossresumebench_v2.mcc import build_mcc_v2, reconstruct_mcc_v2, admissibility, validate_mcc_payload

__all__=["CaseSpec","SourceCapture","build_mcc_v2","reconstruct_mcc_v2","admissibility","validate_mcc_payload","ROOT"]
