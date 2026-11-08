from pathlib import Path
import csv, json
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; GR=RES/'graphs'; GR.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((RES/'pcc_ablation_runs.csv').open(encoding='utf-8')))
ints=['safe_continuation','technical_failure','duplicate_effects','replayed_steps','approval_preserved','retry_preserved','branch_preserved','loop_preserved','parallel_preserved','correct_termination','pcc_bytes']
for r in rows:
    for k in ints: r[k]=int(r[k])
valid=[r for r in rows if not r['technical_failure']]

def group(keys):
    d=defaultdict(list)
    for r in valid: d[tuple(r[k] for k in keys)].append(r)
    return d

def write_summary(name,keys):
    g=group(keys)
    with (RES/name).open('w',newline='',encoding='utf-8') as f:
        fields=keys+['n','safe','scr','duplicate_effects','replayed_steps','mean_pcc_bytes']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for kk,rr in sorted(g.items()):
            n=len(rr); safe=sum(x['safe_continuation'] for x in rr)
            vals=dict(zip(keys,kk)); vals.update(n=n,safe=safe,scr=round(safe/n,6),duplicate_effects=sum(x['duplicate_effects'] for x in rr),replayed_steps=sum(x['replayed_steps'] for x in rr),mean_pcc_bytes=round(sum(x['pcc_bytes'] for x in rr)/n,1))
            w.writerow(vals)

write_summary('condition_summary.csv',['condition'])
write_summary('workflow_condition_summary.csv',['workflow','condition'])
write_summary('pair_condition_summary.csv',['source_framework','target_framework','condition'])

fails=Counter()
for r in valid:
    for x in filter(None,r['failure_types'].split(';')): fails[x]+=1
with (RES/'failure_taxonomy.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['failure_type','count']); w.writerows(fails.most_common())

conditions=json.loads((ROOT/'config'/'experiment.json').read_text(encoding='utf-8'))['conditions']
cond=group(['condition'])
lines=['# PortaFlow PCC v0 — Ablation Evidence Summary','',f'Total configured rows: **{len(rows)}**',f'Valid native target rows: **{len(valid)}**',f'Technical-failure rows: **{len(rows)-len(valid)}**','','## Safe Continuation Rate','']
for c in conditions:
    rr=cond.get((c,),[]); safe=sum(x['safe_continuation'] for x in rr)
    lines.append(f'- **{c}**: {safe}/{len(rr)} = {safe/len(rr):.1%}' if rr else f'- **{c}**: no valid rows')
lines += ['', '## Failure taxonomy','']+[f'- **{k}**: {v}' for k,v in fails.most_common()]
lines += ['', '## Interpretation rule','', 'This deterministic ablation asks which portable semantic components are sufficient for the six declared workflow classes at safe migration boundaries. It does not prove arbitrary process migration or universal coverage of all agent workflows. Full PCC v0 is the proposed mechanism in this experiment; unlike the earlier diagnostic upper bound, it contains no source-native checkpoint blob.']
(RES/'PCC_ABLATION_SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Component marginal gains, computed cumulatively in configured order.
gains=[]; prev=None
for c in conditions:
    rr=cond.get((c,),[])
    if not rr: continue
    scr=sum(x['safe_continuation'] for x in rr)/len(rr)
    gains.append({'condition':c,'scr':scr,'delta_from_previous':None if prev is None else scr-prev})
    prev=scr
(RES/'component_gains.json').write_text(json.dumps(gains,indent=2),encoding='utf-8')

try:
    import matplotlib.pyplot as plt
    labels=[]; vals=[]
    for c in conditions:
        rr=cond.get((c,),[])
        if rr:
            labels.append(c); vals.append(sum(x['safe_continuation'] for x in rr)/len(rr))
    fig=plt.figure(figsize=(10,4.8)); ax=fig.add_subplot(111); ax.bar(labels,vals); ax.set_ylim(0,1.05); ax.set_ylabel('Safe Continuation Rate'); ax.set_title('PCC v0 cumulative ablation'); ax.tick_params(axis='x',rotation=25); fig.tight_layout(); fig.savefig(GR/'pcc_ablation_scr.png',dpi=180); plt.close(fig)

    wg=group(['workflow','condition'])
    workflows=sorted({r['workflow'] for r in valid})
    # one figure per workflow avoids subplots
    for wf in workflows:
        xs=[]; ys=[]
        for c in conditions:
            rr=wg.get((wf,c),[])
            if rr: xs.append(c); ys.append(sum(x['safe_continuation'] for x in rr)/len(rr))
        fig=plt.figure(figsize=(9,4.2)); ax=fig.add_subplot(111); ax.bar(xs,ys); ax.set_ylim(0,1.05); ax.set_ylabel('SCR'); ax.set_title(f'{wf}: PCC component ablation'); ax.tick_params(axis='x',rotation=25); fig.tight_layout(); fig.savefig(GR/f'workflow_{wf}_ablation.png',dpi=180); plt.close(fig)

    if fails:
        names=[k for k,_ in fails.most_common()]; counts=[v for _,v in fails.most_common()]
        fig=plt.figure(figsize=(10,4.5)); ax=fig.add_subplot(111); ax.bar(names,counts); ax.set_ylabel('Failed-run occurrences'); ax.set_title('Failure taxonomy across ablations'); ax.tick_params(axis='x',rotation=30); fig.tight_layout(); fig.savefig(GR/'failure_taxonomy.png',dpi=180); plt.close(fig)
except Exception as e:
    (RES/'graph_error.txt').write_text(str(e),encoding='utf-8')
print('Analysis complete.')
