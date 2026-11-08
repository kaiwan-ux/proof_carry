from __future__ import annotations
from typing import Dict, Any
from .utils import sha256_obj

def contract_from_case(case: Dict[str, Any]) -> Dict[str, Any]:
    # IMPORTANT: the contract states what facts are required and how their values
    # determine continuation. It does not contain the hidden benchmark truth of
    # the decision fact.
    req=[]
    for f in case['required_facts']:
        item={'name':f['name'],'role':f.get('role','guard'),'description':f.get('description','')}
        if item['role']=='guard':
            item['required_value']=f['expected']
        req.append(item)
    decision_fact=req[0]['name']
    contract={
        'version':'proofcarry-contract-v1',
        'workflow_id':case['workflow_id'],
        'case_id':case['case_id'],
        'family':case['workflow_family'],
        'required_facts':req,
        'required_identity':case['required_identity'],
        'dependencies':case.get('dependencies',[]),
        'required_snapshots':case.get('required_snapshots',[]),
        'decision_rule':{
            'fact':decision_fact,
            'plan_if_true':case['safe_plan'],
            'plan_if_false':case['alternate_plan'],
        },
    }
    contract['contract_hash']=sha256_obj(contract)
    return contract
