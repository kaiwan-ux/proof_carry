from __future__ import annotations
import json, re
from collections import Counter
from pathlib import Path

def audit(root: Path):
    cases=[json.loads(x) for x in (root/'benchmark/cases/all_cases.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    fam=Counter(c['workflow_family'] for c in cases)
    fields=['case_id','scenario_kind','title','description']
    duplicate_fields={k:len(cases)-len({c[k] for c in cases}) for k in fields}
    fact_fingerprints=[]
    for c in cases:
        fact_fingerprints.append(tuple(sorted(f['name'].split('.',1)[-1] for f in c['required_facts'])))
    checks={
        'exact_total_120':len(cases)==120,
        'eight_families':len(fam)==8,
        'fifteen_each':all(v==15 for v in fam.values()),
        'unique_case_ids':duplicate_fields['case_id']==0,
        'unique_scenario_kinds':duplicate_fields['scenario_kind']==0,
        'unique_titles':duplicate_fields['title']==0,
        'unique_descriptions':duplicate_fields['description']==0,
        'all_have_3plus_required_facts':all(len(c['required_facts'])>=3 for c in cases),
        'all_have_dependencies':all(c.get('dependencies') for c in cases),
        'all_have_safe_plan':all(c.get('safe_plan') for c in cases),
    }
    return {'pass':all(checks.values()),'checks':checks,'family_counts':dict(fam),'duplicate_fields':duplicate_fields,'note':'Uniqueness audit rejects exact duplicate scenario concepts/text. Scientific diversity remains a design property documented in CASE_DESIGN_NOTES.md.'}
if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); a=ap.parse_args(); print(json.dumps(audit(Path(a.root)),indent=2))
