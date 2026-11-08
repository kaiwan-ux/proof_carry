from pathlib import Path
import zipfile,json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/"results"; out=ROOT/"CrossResumeBench_MCCv3_Holdout_NATIVE_GATE_diagnostics.zip"
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for name in ["NATIVE_FAMILY_GATE.json","native_family_gate.csv"]:
        p=R/name
        if p.exists(): z.write(p,p.relative_to(ROOT))
    for p in sorted((R/"work").rglob("*")) if (R/"work").exists() else []:
        if p.is_file() and p.name.endswith((".txt",".json")): z.write(p,p.relative_to(ROOT))
print(out)
