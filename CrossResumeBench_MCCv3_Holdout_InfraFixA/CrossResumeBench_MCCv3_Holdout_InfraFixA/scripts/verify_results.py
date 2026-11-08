import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'
with (R/'migration_runs.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
assert len(rows)==6144,len(rows)
with (R/'self_resume.csv').open(encoding='utf-8') as f: s=list(csv.DictReader(f)); assert len(s)==96
with (R/'source_captures.csv').open(encoding='utf-8') as f: c=list(csv.DictReader(f)); assert len(c)==96
assert sum(int(r['technical_failure']) for r in rows)==0
print('RESULT_STRUCTURE_OK',len(rows))
