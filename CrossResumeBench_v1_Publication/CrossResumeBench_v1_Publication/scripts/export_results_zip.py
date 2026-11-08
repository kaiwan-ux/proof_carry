from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'CrossResumeBench_v1_results'; p=shutil.make_archive(str(out),'zip',ROOT,'results'); print(p)
