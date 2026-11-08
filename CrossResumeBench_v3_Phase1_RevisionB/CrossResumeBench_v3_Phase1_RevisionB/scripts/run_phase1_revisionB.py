from pathlib import Path
import shutil, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_v3_revb.runner import run

for p in ROOT.joinpath("results").glob("*"):
    if p.name in {"artifacts","native_sources","native_targets","work"}:
        shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
    elif p.is_file(): p.unlink()
run(ROOT/"results")
print("Phase 1 Revision B execution complete")
