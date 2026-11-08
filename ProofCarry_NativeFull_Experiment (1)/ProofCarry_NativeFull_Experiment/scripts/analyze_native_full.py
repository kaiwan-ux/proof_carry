from __future__ import annotations
import argparse,csv,json,statistics,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read_csv(p):
    with Path(p).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))

def asint(v):
    try:return int(v)
    except:return 0

def summarize(rows,keys):
    groups=defaultdict(list)
    for r in rows: groups[tuple(r[k] for k in keys)].append(r)
    out=[]
    for kk,rs in sorted(groups.items()):
        d=dict(zip(keys,kk)); n=len(rs)
        d.update(rows=n,safe_completion=sum(asint(x.get('safe_completion')) for x in rs),safe_rejection=sum(asint(x.get('safe_rejection')) for x in rs),unsafe=sum(asint(x.get('unsafe_violation')) for x in rs),technical=sum(asint(x.get('technical_failure')) for x in rs))
        denom=max(1,n-d['technical']); d['unsafe_rate_nontechnical']=d['unsafe']/denom; d['safe_completion_rate_nontechnical']=d['safe_completion']/denom
        out.append(d)
    return out

def write_csv(p,rows):
    if not rows:return
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys:keys.append(k)
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run_dir');args=ap.parse_args();d=Path(args.run_dir)
    rows=read_csv(d/'native_runs.csv')
    for name,keys in [('native_method_summary.csv',['method']),('native_pair_summary.csv',['source','target','method']),('native_family_summary.csv',['family','method']),('native_condition_summary.csv',['condition','method'])]:write_csv(d/name,summarize(rows,keys))
    gate=read_csv(d/'native_family_gate.csv'); selfr=read_csv(d/'native_self_resume.csv'); caps=read_csv(d/'native_source_captures.csv')
    methods=summarize(rows,['method'])
    pairpc=[r for r in summarize(rows,['source','target','method']) if r['method']=='proofcarry']
    verdict={
      'migration_rows':len(rows),
      'technical_failures':sum(asint(r.get('technical_failure')) for r in rows),
      'framework_gate':{fw:{'passed':sum(asint(r['pass']) for r in gate if r['framework']==fw),'total':sum(1 for r in gate if r['framework']==fw)} for fw in sorted(set(r['framework'] for r in gate))},
      'self_resume':{fw:{'safe':sum(asint(r['safe']) for r in selfr if r['framework']==fw),'technical':sum(asint(r['technical_failure']) for r in selfr if r['framework']==fw),'total':sum(1 for r in selfr if r['framework']==fw)} for fw in sorted(set(r['framework'] for r in selfr))},
      'source_capture':{fw:{'success':sum(asint(r['capture_success']) for r in caps if r['framework']==fw),'technical':sum(asint(r['technical_failure']) for r in caps if r['framework']==fw),'total':sum(1 for r in caps if r['framework']==fw)} for fw in sorted(set(r['framework'] for r in caps))},
      'methods':methods,
      'proofcarry_pairs':pairpc,
    }
    all_gate=all(v['passed']==v['total'] and v['total']>0 for v in verdict['framework_gate'].values())
    pc=next((x for x in methods if x['method']=='proofcarry'),None)
    verdict['all_three_native_family_gates_pass']=all_gate
    pc_nontechnical=(pc['rows']-pc['technical']) if pc else 0
    verdict['proofcarry_nontechnical_rows']=pc_nontechnical
    verdict['proofcarry_zero_observed_unsafe']=bool(pc and pc_nontechnical>0 and pc['unsafe']==0)
    gate_pass_total=sum(v['passed'] for v in verdict['framework_gate'].values())
    if gate_pass_total==0:
        verdict['claim_level']='NATIVE_ENVIRONMENT_UNAVAILABLE'
    elif all_gate and verdict['technical_failures']==0:
        verdict['claim_level']='THREE_RUNTIME_NATIVE_MATRIX'
    else:
        verdict['claim_level']='PARTIAL_NATIVE_REPRODUCIBILITY'
    (d/'NATIVE_RESEARCH_VERDICT.json').write_text(json.dumps(verdict,indent=2,sort_keys=True),encoding='utf-8')
    lines=['# ProofCarry NativeFull Analysis','',f"Migration rows: **{len(rows):,}**",f"Technical rows: **{verdict['technical_failures']:,}**",'', '## Framework family gates']
    for fw,v in verdict['framework_gate'].items():lines.append(f"- {fw}: {v['passed']}/{v['total']}")
    lines+=['','## ProofCarry']
    if pc:lines.append(f"- safe completion: {pc['safe_completion']:,}; safe rejection: {pc['safe_rejection']:,}; unsafe: {pc['unsafe']:,}; technical: {pc['technical']:,}")
    lines+=['',f"**Claim level:** `{verdict['claim_level']}`",'', '> Native technical failures are never converted into semantic failures or successes. Semantic and native studies remain separate evidence layers.']
    (d/'NATIVE_ANALYSIS_SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
if __name__=='__main__':main()
