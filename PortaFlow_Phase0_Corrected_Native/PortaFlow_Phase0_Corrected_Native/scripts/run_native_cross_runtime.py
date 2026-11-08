from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from portaflow_native.orchestrator import run

if __name__=="__main__":
    cfg=json.loads((ROOT/"config/experiment.json").read_text(encoding="utf-8"))
    recs=run(cfg,ROOT)
    print(f"Native cross-runtime rows: {len(recs)}")
    print(f"Technical failures: {sum(r.technical_failure for r in recs)}")
