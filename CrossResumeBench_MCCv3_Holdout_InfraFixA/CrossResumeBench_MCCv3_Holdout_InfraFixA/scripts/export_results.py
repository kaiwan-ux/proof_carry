from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; out=ROOT/'CrossResumeBench_MCCv3_Holdout_results.zip'
manifest={}
for p in sorted(R.rglob('*')):
    if p.is_file(): manifest[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'RESULT_MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf-8')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(R.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(ROOT))
    for p in [ROOT/'benchmark/HOLDOUT_SEAL.json',ROOT/'benchmark/HOLDOUT_SUITE_SHA256.txt',ROOT/'mechanism/MCCV3_FREEZE_RECORD.json',ROOT/'discovery/DISCOVERY_RECORD.json']:
        z.write(p,p.relative_to(ROOT))
print(out)
