from __future__ import annotations
import copy, itertools
from typing import Dict, Any
from .contracts import contract_from_case
from .types import RuntimeContext
from .certificates import issue_certificate, DEFAULT_TEST_KEY
from .runtime_repr import identity_mapping, build_runtime_state

_counter = itertools.count(1)

def _flip(v):
    if isinstance(v,bool): return not v
    if isinstance(v,int): return v + 1
    if v is None: return "unexpected"
    return f"WRONG::{v}"

def build_evidence(case: Dict[str, Any], source: str, target: str, variant: str,
                   key: bytes=DEFAULT_TEST_KEY) -> Dict[str, Any]:
    contract=contract_from_case(case)
    ctx=RuntimeContext(case["workflow_id"], case["execution_id"], source, target, contract["contract_hash"])
    history={}
    certs=[]
    snapshots={'obligations':{'complete':True,'members':{},'universe':[]}}
    for i,f in enumerate(case["required_facts"]):
        src=f.get("source","history")
        if src == "history":
            history[f["name"]]=f["expected"]
        elif src == "certificate":
            certs.append(issue_certificate(subject=f["name"], value=f["expected"], context=ctx,
                         nonce=f"{case['case_id']}:{source}:{target}:{i}", issuer=f.get("issuer","trusted-runtime-witness"), key=key))
        elif src == "snapshot":
            group=f.get("snapshot","obligations")
            snap=snapshots.setdefault(group,{"complete":True,"members":{},"universe":[]})
            snap["members"][f["name"]]=f["expected"]
            snap["universe"].append(f["name"])
        else:
            raise ValueError(src)
    # Supporting dependency facts are evidence but are not themselves the decision target.
    for i,f in enumerate(case.get('support_facts',[]), start=100):
        if f.get('source') == 'history':
            history[f['name']]=f['truth']
        else:
            certs.append(issue_certificate(subject=f['name'], value=f['truth'], context=ctx, nonce=f"{case['case_id']}:{source}:{target}:support:{i}", key=key))
    mapping=identity_mapping(case,source,target,"correct")
    ev={
        "case_id":case["case_id"],
        "source_runtime":source,
        "target_runtime":target,
        "source_state":build_runtime_state(case,source),
        "history":history,
        "certificates":certs,
        "snapshots":snapshots,
        "identity_mapping":mapping,
        "noise":{},
    }
    critical=case["required_facts"][0]
    if variant == "enough":
        pass
    elif variant == "irrelevant_noise":
        ev["noise"]={f"noise_{j}":f"irrelevant-{case['case_id']}-{j}" for j in range(12)}
    elif variant == "missing_critical":
        name=critical["name"]
        ev["history"].pop(name,None)
        ev["certificates"]=[c for c in ev["certificates"] if c.get("subject")!=name]
        for s in ev["snapshots"].values():
            s["members"].pop(name,None)
    elif variant == "contradictory_fact":
        # Keep correct evidence and add a second, valid but conflicting observation.
        name=critical["name"]
        ev["history"][name]=critical["expected"]
        ev["certificates"].append(issue_certificate(subject=name, value=_flip(critical["expected"]), context=ctx,
                   nonce=f"{case['case_id']}:{source}:{target}:conflict", key=key))
    elif variant == "identity_missing":
        ev["identity_mapping"]=identity_mapping(case,source,target,"missing")
    elif variant == "dependency_unresolved":
        if case.get("dependencies"):
            dep=case["dependencies"][0]["requires"]
            ev["history"].pop(dep,None)
            ev["certificates"]=[c for c in ev["certificates"] if c.get("subject")!=dep]
            for s in ev["snapshots"].values(): s["members"].pop(dep,None)
        else:
            ev["history"].pop(critical["name"],None)
    elif variant == "incomplete_snapshot":
        if ev["snapshots"]:
            for s in ev["snapshots"].values(): s["complete"]=False
        else:
            # Introduce a required complete snapshot not available.
            ev["snapshots"]["obligations"]={"complete":False,"members":{},"universe":["none_pending"]}
    else:
        raise ValueError(variant)
    return ev
