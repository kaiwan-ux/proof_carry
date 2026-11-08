from __future__ import annotations
import hashlib, json
from pathlib import Path

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main(root=Path('.')):
 p=root/'legacy_evidence/sealed_holdout_32/migration_runs.csv'
 import pandas as pd
 df=pd.read_csv(p)
 checks={'migration_rows_6144':len(df)==6144,'base_cases_32':df.case_id.nunique()==32,'methods_8':df.method.nunique()==8,'sha256':sha(p)}
 print(json.dumps(checks,indent=2)); return all(v for k,v in checks.items() if isinstance(v,bool))
if __name__=='__main__': raise SystemExit(0 if main() else 1)
