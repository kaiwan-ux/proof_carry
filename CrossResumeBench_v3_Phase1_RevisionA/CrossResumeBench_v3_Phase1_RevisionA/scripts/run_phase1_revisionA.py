from pathlib import Path
import sys,shutil
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_v3_reva.runner import run
# Clean generated result files but preserve directory skeleton.
for p in ROOT.joinpath("results").glob("*"):
    if p.name in {"artifacts","native_sources","native_targets","work"}: shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
    elif p.is_file(): p.unlink()
run(ROOT/"results")
print("Phase1 Revision A execution complete")
