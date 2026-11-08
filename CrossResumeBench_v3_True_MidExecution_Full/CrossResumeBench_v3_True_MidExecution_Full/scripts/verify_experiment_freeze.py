from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/"benchmark"/"FREEZE_RECORD.json").read_text(encoding="utf-8"))
bad=[]
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
if sha("benchmark/generated_suite.json")!=r["generated_suite_file_sha256"]: bad.append("generated_suite.json")
if sha("benchmark/EVIDENCE_APPLICABILITY.json")!=r["evidence_applicability_sha256"]: bad.append("EVIDENCE_APPLICABILITY.json")
h=hashlib.sha256()
for rel in r["evaluation_files"]:
    h.update(rel.encode()); h.update(b"\0"); h.update((ROOT/rel).read_bytes()); h.update(b"\0")
if h.hexdigest()!=r["evaluation_code_combined_sha256"]: bad.append("evaluation_code")
print(json.dumps({"ok":not bad,"bad":bad,"freeze_record":r},indent=2))
raise SystemExit(0 if not bad else 6)
