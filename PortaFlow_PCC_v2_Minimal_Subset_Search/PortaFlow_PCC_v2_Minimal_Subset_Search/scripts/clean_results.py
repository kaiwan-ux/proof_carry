from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]/"results"
for p in R.iterdir():
    if p.name=="README.md": continue
    if p.is_dir(): shutil.rmtree(p)
    else: p.unlink()
for d in ["graphs","native_sources","native_targets","capsules","inference_reports","probes"]:(R/d).mkdir(parents=True,exist_ok=True)
for d in ["graphs","native_sources","native_targets","capsules","inference_reports","probes"]:
    (R/d/".gitkeep").write_text("")
print("Clean results directory ready.")
