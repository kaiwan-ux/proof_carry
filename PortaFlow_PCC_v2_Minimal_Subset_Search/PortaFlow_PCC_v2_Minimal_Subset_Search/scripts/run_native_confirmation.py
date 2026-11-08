from pathlib import Path
import json
from portaflow_min.native import run_native
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'config/experiment.json').read_text())
sel=json.loads((ROOT/'results/selected_native_conditions.json').read_text())
rows=run_native(cfg,ROOT,sel)
print(f"Native confirmation rows: {len(rows)}")
