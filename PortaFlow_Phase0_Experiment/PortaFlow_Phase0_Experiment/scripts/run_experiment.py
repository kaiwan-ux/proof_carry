from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from portaflow_phase0.runner import run_matrix
from portaflow_phase0.utils import load_config


def main() -> int:
    cfg = load_config(ROOT)
    (ROOT / "results" / "CONFIG_SNAPSHOT.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    records = run_matrix(cfg, ROOT)
    print(f"Controlled Phase-0 matrix complete: {len(records)} runs")
    print(f"Raw results: {ROOT / 'results' / 'raw_runs.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
