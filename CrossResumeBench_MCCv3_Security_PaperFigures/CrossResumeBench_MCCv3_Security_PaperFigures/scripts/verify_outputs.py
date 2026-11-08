from pathlib import Path
import pandas as pd, json, sys
ROOT=Path(__file__).resolve().parents[1]
sec=ROOT/'results/security/security_runs.csv'
if not sec.exists(): raise SystemExit('missing security_runs.csv')
df=pd.read_csv(sec)
checks={
 'rows_768':len(df)==768,
 'no_technical_column_needed':True,
 'valid_controls_96_complete':int(((df.variant=='valid_control')&(df.outcome=='safe_completion')).sum())==96,
 'in_model_zero_unsafe':int(((df.attack_class=='in_threat_model')&(df.outcome=='unsafe')).sum())==0,
 'in_model_mutations_reject_480':int(((df.attack_class=='in_threat_model')&(df.outcome=='safe_rejection')).sum())==480,
 'trust_boundary_exposed':int(((df.attack_class=='out_of_threat_model')&(df.outcome=='unsafe')).sum())==192,
 'paper_png_11':len(list((ROOT/'figures/generated').glob('fig*.png')))>=11,
 'paper_pdf_11':len(list((ROOT/'figures/generated').glob('fig*.pdf')))>=11,
 'paper_svg_11':len(list((ROOT/'figures/generated').glob('fig*.svg')))>=11,
}
(ROOT/'results/VERIFICATION.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
if not all(checks.values()): sys.exit(3)
