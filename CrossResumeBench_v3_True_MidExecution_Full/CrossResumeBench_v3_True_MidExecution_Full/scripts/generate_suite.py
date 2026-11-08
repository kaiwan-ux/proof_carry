from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2"/"src")]
from crossresumebench_v3_full.cases import suite_dict,suite_hash
p=ROOT/"benchmark"/"generated_suite.json"
p.write_text(json.dumps(suite_dict(),indent=2),encoding="utf-8")
(ROOT/"benchmark"/"FROZEN_FULL_SUITE_SHA256.txt").write_text(suite_hash()+"\n",encoding="utf-8")
print(suite_hash())
