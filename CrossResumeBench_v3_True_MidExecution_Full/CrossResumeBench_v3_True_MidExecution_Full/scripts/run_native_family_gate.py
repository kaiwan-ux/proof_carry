from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2"/"src")]
from crossresumebench_v3_full.runner import native_family_gate
ok=native_family_gate(ROOT/"results"); raise SystemExit(0 if ok else 4)
