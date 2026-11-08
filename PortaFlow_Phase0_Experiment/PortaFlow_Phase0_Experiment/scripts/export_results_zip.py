from __future__ import annotations
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=shutil.make_archive(str(ROOT/"PortaFlow_Phase0_RESULTS"),"zip",root_dir=ROOT,base_dir="results")
print(out)
