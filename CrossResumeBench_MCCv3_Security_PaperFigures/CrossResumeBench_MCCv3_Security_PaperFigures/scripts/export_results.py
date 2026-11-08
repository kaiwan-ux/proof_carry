from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'CrossResumeBench_MCCv3_Security_PaperFigures_results.zip'
include=[ROOT/'results',ROOT/'figures/generated',ROOT/'figures/data',ROOT/'figures/PAPER_FIGURE_CAPTIONS.md',ROOT/'docs/PAPER_FIGURE_SELECTION.md',ROOT/'docs/CLAIM_BOUNDARIES.md']
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for item in include:
        if item.is_file(): z.write(item,item.relative_to(ROOT))
        elif item.exists():
            for p in item.rglob('*'):
                if p.is_file(): z.write(p,p.relative_to(ROOT))
print(out)
