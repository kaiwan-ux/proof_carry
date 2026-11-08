from pathlib import Path
import json
from portaflow_robust.native import run_native
from portaflow_robust.conditions import FROZEN_CONDITIONS
ROOT=Path(__file__).resolve().parents[1]; cfg=json.loads((ROOT/'config/experiment.json').read_text()); rows=run_native(cfg,ROOT,FROZEN_CONDITIONS); print(f'Native robustness rows: {len(rows)}')
