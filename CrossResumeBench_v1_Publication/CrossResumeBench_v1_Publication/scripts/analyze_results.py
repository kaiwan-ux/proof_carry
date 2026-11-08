from pathlib import Path
from crossresumebench.analysis import summarize
ROOT=Path(__file__).resolve().parents[1]; summarize(ROOT); print('analysis complete')
