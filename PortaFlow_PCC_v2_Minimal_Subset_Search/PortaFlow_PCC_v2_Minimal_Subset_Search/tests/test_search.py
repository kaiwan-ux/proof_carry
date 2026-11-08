from collections import defaultdict
from portaflow_min.search import exhaustive_rows,choose_minimal

def _agg():
    rows=exhaustive_rows(); d={}
    for x in rows:
        k=(x.inference_mode,x.subset_key,x.components,x.component_count); a=d.setdefault(k,{'inference_mode':x.inference_mode,'subset_key':x.subset_key,'components':x.components,'component_count':x.component_count,'cases':0,'safe_completions':0,'rejections':0,'unsafe_violations':0,'bytes':[]})
        a['cases']+=1;a['safe_completions']+=x.safe_completion;a['rejections']+=x.migration_rejected;a['unsafe_violations']+=x.unsafe_violation;a['bytes'].append(x.capsule_bytes)
    out=[]
    for a in d.values():
        b={k:v for k,v in a.items() if k!='bytes'};b['mean_capsule_bytes']=sum(a['bytes'])/len(a['bytes']);out.append(b)
    return out

def test_search_finds_full_coverage_candidates():
    a=_agg(); assert choose_minimal(a,'explicit') is not None; assert choose_minimal(a,'hybrid') is not None

def test_hybrid_candidate_is_no_larger_than_explicit_candidate():
    a=_agg(); e=choose_minimal(a,'explicit'); h=choose_minimal(a,'hybrid'); assert h['component_count']<=e['component_count']
