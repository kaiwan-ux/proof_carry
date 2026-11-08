# CrossResumeBench — MCC v3 Security Stress + Paper Figures

This package is the final experimental/visualization stage before the architecture diagram and paper draft.

It **does not modify MCC v3**, the sealed holdout, or the post-validation statistics. It adds:

1. A targeted attestation-integrity / trust-boundary stress test.
2. Reproducible publication figures from the already-passed holdout and post-validation studies.
3. Vector PDF + SVG and 600-DPI PNG exports.
4. Figure source-data CSVs and suggested paper captions.

## Scientific separation

- `inputs/postvalidation/` = immutable evidence from the passed MCC v3 study.
- `mechanism/` = frozen MCC v3 mechanism copied from the validated package.
- `studies/security/` = new mechanism-level security stress test.
- `figures/generated/` = publication-ready figures.
- `figures/data/` = exact source data used to render each figure.

The security study is **not** a new native-runtime safety holdout. It specifically tests evidence integrity and the trusted-witness boundary.

## Run everything

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_security_figures.ps1
```

Outputs:
- `results/security/security_runs.csv`
- `results/security/SECURITY_VERDICT.json`
- `results/security/SECURITY_REPORT.md`
- `figures/generated/*.pdf|*.svg|*.png`
- `CrossResumeBench_MCCv3_Security_PaperFigures_results.zip`

Read `docs/PAPER_FIGURE_SELECTION.md` before choosing figures for the main paper.
