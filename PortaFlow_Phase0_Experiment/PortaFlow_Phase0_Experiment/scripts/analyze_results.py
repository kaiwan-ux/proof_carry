from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from portaflow_phase0.reporting import analyze

if __name__ == "__main__":
    analyze(ROOT)
    print(f"Analysis complete: {ROOT / 'results' / 'ANALYSIS_SUMMARY.md'}")
