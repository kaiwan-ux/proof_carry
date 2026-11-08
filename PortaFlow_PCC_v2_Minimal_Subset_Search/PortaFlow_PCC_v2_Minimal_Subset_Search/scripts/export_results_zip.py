from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'PortaFlow_PCC_v2_minimal_subset_results'
zip_path=Path(shutil.make_archive(str(out),'zip',root_dir=ROOT,base_dir='results'))
print(zip_path)
