from pathlib import Path
import shutil, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_v3_revc.runner import run

# Preserve preflight and MAF-pre-gate evidence in the full exported result package.
preserve={"MAF_REVISIONC_PROBE.json","capabilities.json"}
for p in ROOT.joinpath("results").glob("*"):
    if p.name in {"artifacts","native_sources","native_targets","work","maf_probe_work"}:
        if p.name != "maf_probe_work":
            shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
    elif p.is_file() and p.name not in preserve:
        p.unlink()
run(ROOT/"results")
print("Phase 1 Revision C execution complete")
