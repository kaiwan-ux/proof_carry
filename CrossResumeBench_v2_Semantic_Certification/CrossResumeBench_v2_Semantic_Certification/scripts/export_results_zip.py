from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'CrossResumeBench_v2_results';
if out.with_suffix('.zip').exists(): out.with_suffix('.zip').unlink()
shutil.make_archive(str(out),'zip',root_dir=ROOT,base_dir='results'); print(out.with_suffix('.zip'))
