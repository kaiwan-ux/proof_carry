from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'native_gate_results'; out=ROOT/'CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(R.rglob('*')) if R.exists() else []:
        if p.is_file(): z.write(p,p.relative_to(ROOT))
    for rel in ['INFRAFIXA_RECORD.json','benchmark/HOLDOUT_SEAL.json','benchmark/HOLDOUT_SUITE_SHA256.txt','mechanism/MCCV3_FREEZE_RECORD.json','benchmark/EXPERIMENT_FREEZE_RECORD.json']:
        p=ROOT/rel
        if p.exists(): z.write(p,p.relative_to(ROOT))
print(out)
