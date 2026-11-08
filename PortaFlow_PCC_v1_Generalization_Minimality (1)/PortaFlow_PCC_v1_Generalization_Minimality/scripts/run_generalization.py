import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from portaflow_v1.orchestrator import run
cfg=json.loads((ROOT/"config"/"experiment.json").read_text(encoding="utf-8"))
rows=run(cfg,ROOT); print(f"Generated {len(rows)} rows.")
