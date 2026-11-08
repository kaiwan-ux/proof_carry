from _bootstrap import *
from pathlib import Path
import zipfile
from studies.common import ROOT
out=ROOT/'CrossResumeBench_MCCv3_PostValidation_results.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in (ROOT/'results').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT))
    for p in (ROOT/'inputs'/'passed_holdout').glob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT))
print(out)
