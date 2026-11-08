import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from crossresumebench_proofcarry.performance_study import run
ap=argparse.ArgumentParser(); ap.add_argument('--repeats',type=int,default=5); a=ap.parse_args(); run(ROOT/'results',a.repeats)
