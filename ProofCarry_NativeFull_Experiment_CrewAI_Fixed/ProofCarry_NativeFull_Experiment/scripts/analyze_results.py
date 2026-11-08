import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from crossresumebench_proofcarry.analysis import analyze
print(analyze(ROOT/'results'))
