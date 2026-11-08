from __future__ import annotations
import csv, json, hashlib, copy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from mechanism.mcc_v3 import build_mcc_v3, resolve_proofs, _hash_evidence

SUITE = json.loads((ROOT/'studies/security/security_suite.json').read_text(encoding='utf-8'))
MECH_ROOT = ROOT/'mechanism'
OUT = ROOT/'results/security'
OUT.mkdir(parents=True, exist_ok=True)


def cert(case, value=None, subject=None, evidence=None, cert_id=None):
    value = case['truth_value'] if value is None else value
    subject = case['subject'] if subject is None else subject
    evidence = {'witness':'security_suite','case_context':case['case_id']} if evidence is None else evidence
    c = {
        'certificate_id': cert_id or f"cert-{case['case_id']}",
        'fact_type': case['certificate_fact_type'],
        'subject': subject,
        'value': value,
        'scope': 'workflow',
        'evidence': evidence,
        'issuer': 'trusted_witness_reference',
    }
    c['evidence_hash'] = _hash_evidence(c['fact_type'], c['subject'], c['value'], c['scope'], c['evidence'])
    return c


def contract(case):
    return {'contract_version':'1.0','required_facts':[{
        'fact_type':case['required_fact_type'],'subject':case['subject'],
        'purpose':'security-critical continuation decision'
    }]}


def spec_hash(case):
    return hashlib.sha256((case['workflow']+'|security-v1').encode()).hexdigest()


def outcome_from_ps(case, ps, admiss):
    if not admiss['admissible']:
        return 'safe_rejection', '', admiss.get('reason','')
    got = ps.get(case['required_fact_type'], case['subject'])
    if got == case['truth_value']:
        return 'safe_completion', got, ''
    return 'unsafe', got, 'ADMITTED_WRONG_CONTINUATION_FACT'


def run_one(case, source, target, variant, pair_case):
    base_cert = cert(case)
    capture = {
        'case_id':case['case_id'],'workflow':case['workflow'],'app_state':{},'history':[],
        'certificates':[base_cert], 'native_observation':{'framework':source}
    }
    payload = build_mcc_v3(capture, target, spec_hash(case), contract(case), MECH_ROOT)
    attack_class='in_threat_model'
    expected='safe_completion' if variant=='valid_control' else 'safe_rejection'

    if variant == 'value_tamper_no_rehash':
        payload['certificates'][0]['value'] = case['unsafe_value']
    elif variant == 'subject_tamper_no_rehash':
        payload['certificates'][0]['subject'] = case['subject'] + '__tampered'
    elif variant == 'evidence_tamper_no_rehash':
        payload['certificates'][0]['evidence']['case_context'] = 'tampered-context'
    elif variant == 'contract_hash_tamper':
        payload['continuation_contract_hash'] = '0'*64
    elif variant == 'conflicting_valid_certificates':
        payload['certificates'].append(cert(case, value=case['unsafe_value'], cert_id='conflict-'+case['case_id']))
    elif variant == 'cross_context_replay':
        attack_class='out_of_threat_model'
        expected='unsafe_expected_trust_boundary'
        payload['certificates'] = [cert(pair_case)]
    elif variant == 'forged_rehash_wrong_value':
        attack_class='out_of_threat_model'
        expected='unsafe_expected_trust_boundary'
        payload['certificates'] = [cert(case, value=case['unsafe_value'], evidence={'witness':'attacker_rehashed','case_context':case['case_id']})]
    elif variant == 'valid_control':
        pass
    else:
        raise ValueError(variant)

    ps, admiss = resolve_proofs(payload, contract(case), MECH_ROOT)
    outcome, resolved_value, reason = outcome_from_ps(case, ps, admiss)
    return {
        'case_id':case['case_id'],'family':case['family'],'source':source,'target':target,
        'variant':variant,'attack_class':attack_class,'expected_policy':expected,'outcome':outcome,
        'admissible':int(admiss['admissible']),'resolved_value':json.dumps(resolved_value, ensure_ascii=False),
        'truth_value':json.dumps(case['truth_value'], ensure_ascii=False),'unsafe_value':json.dumps(case['unsafe_value'], ensure_ascii=False),
        'reason':reason,'invalid_attestations':len(ps.invalid_attestations),'conflicts':len(ps.conflicts),
        'unresolved':len(ps.unresolved)
    }


def main():
    cases={c['case_id']:c for c in SUITE['cases']}
    rows=[]
    for case in SUITE['cases']:
        pair=cases[case['pair_case_id']]
        for source,target in SUITE['runtime_pairs']:
            for variant in SUITE['attack_variants']:
                rows.append(run_one(case, source, target, variant, pair))
    csv_path=OUT/'security_runs.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter, defaultdict
    summary=Counter(r['outcome'] for r in rows)
    by_variant={}
    for v in SUITE['attack_variants']:
        rr=[r for r in rows if r['variant']==v]
        by_variant[v]=dict(Counter(r['outcome'] for r in rr))
    by_class={}
    for c in ['in_threat_model','out_of_threat_model']:
        rr=[r for r in rows if r['attack_class']==c]
        by_class[c]=dict(Counter(r['outcome'] for r in rr))
    report={
        'suite_version':SUITE['suite_version'],'rows':len(rows),'summary':dict(summary),
        'by_variant':by_variant,'by_attack_class':by_class,
        'in_model_integrity_gate_pass': all(r['outcome'] in {'safe_completion','safe_rejection'} for r in rows if r['attack_class']=='in_threat_model'),
        'trust_boundary_exposed': any(r['outcome']=='unsafe' for r in rows if r['attack_class']=='out_of_threat_model'),
        'claim_boundary':'Hash integrity detects non-rehashed mutation, but does not authenticate issuer authority or bind certificates to a unique case/context. Out-of-model forged/replayed valid hashes are expected to expose this boundary.'
    }
    (OUT/'SECURITY_VERDICT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=['# MCC v3 Security Stress Report','',f"- Rows: {len(rows)}",f"- In-threat-model integrity gate: **{'PASS' if report['in_model_integrity_gate_pass'] else 'FAIL'}**",f"- Trust boundary exposed by out-of-model attacks: **{report['trust_boundary_exposed']}**",'', '## Outcomes']
    for k,v in summary.items(): md.append(f'- {k}: {v}')
    md += ['', '## By variant']
    for k,v in by_variant.items(): md.append(f'- {k}: {v}')
    md += ['', '## Interpretation', report['claim_boundary']]
    (OUT/'SECURITY_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
