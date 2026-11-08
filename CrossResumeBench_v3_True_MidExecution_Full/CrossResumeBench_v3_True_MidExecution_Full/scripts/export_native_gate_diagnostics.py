from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/"CrossResumeBench_v3_Full_NATIVE_GATE_diagnostics.zip"; r=ROOT/"results"
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted(r.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT))
print(out)
