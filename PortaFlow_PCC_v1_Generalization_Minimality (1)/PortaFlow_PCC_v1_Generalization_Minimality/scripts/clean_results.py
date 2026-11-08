from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/"results"
keep={"README.md"}
for p in sorted(R.rglob("*"),reverse=True):
    if p.is_file() and p.name not in keep and p.name!=".gitkeep": p.unlink()
for d in ["capsules","inference_reports","native_sources","native_targets","probes","graphs"]:
    (R/d).mkdir(parents=True,exist_ok=True); (R/d/".gitkeep").touch()
print("Clean results directory prepared.")
