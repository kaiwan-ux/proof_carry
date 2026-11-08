from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2/src')]
from crossresumebench_v3.runner import run
run(ROOT/'results')
print('Phase 1 execution finished.')
