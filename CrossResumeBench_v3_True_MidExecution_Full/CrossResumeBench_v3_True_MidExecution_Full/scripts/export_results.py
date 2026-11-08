from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/"CrossResumeBench_v3_Full_results.zip"; r=ROOT/"results"
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted(r.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT))
    for p in [ROOT/"benchmark"/"generated_suite.json",ROOT/"benchmark"/"FROZEN_FULL_SUITE_SHA256.txt",ROOT/"frozen_v2"/"REVISIONC_FROZEN_HASHES.json",ROOT/"config"/"full_v3.json",ROOT/"benchmark"/"FREEZE_RECORD.json",ROOT/"benchmark"/"EVIDENCE_APPLICABILITY.json"]:
        z.write(p,p.relative_to(ROOT))
print(out)
