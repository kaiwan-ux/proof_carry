from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
for p in [ROOT,ROOT/'src',ROOT/'frozen_v2'/'src']:
    if str(p) not in sys.path: sys.path.insert(0,str(p))
