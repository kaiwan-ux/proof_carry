from __future__ import annotations
from crossresumebench_v2.models import SourceCapture,CaseSpec

def to_source_capture(c):
    return SourceCapture(c['case_id'],c['workflow'],c['app_state'],c['history'],c['certificates'],{},c['native_observation'])
def v2_case_spec(case):
    actions=[]; deps={}
    def comp(kind,p):
        nonlocal actions,deps
        if kind=='effect_commitment': actions += [{'action_id':'effect_guard','semantic_unit':p['effect_unit'],'kind':'effect','operation':p['operation']},{'action_id':p['ack_unit'],'semantic_unit':p['ack_unit'],'kind':'step'}]
        elif kind=='retry_pause': actions += [{'action_id':p['retry_unit'],'semantic_unit':p['retry_unit'],'kind':'step'}]
        elif kind=='approval_wait': actions += [{'action_id':p['request_id'],'semantic_unit':p['approval_unit'],'kind':'approval'}]
        elif kind=='parallel_join': actions += [{'action_id':b,'semantic_unit':b,'kind':'step'} for b in p['branches']]+[{'action_id':p['join'],'semantic_unit':p['join'],'kind':'join'}]; deps[p['join']]=list(p['branches'])
        elif kind=='loop_pause': actions += [{'action_id':'loop_body','semantic_unit':'loop_body','kind':'step'}]
        elif kind=='compensation_pending': actions += [{'action_id':'effect_guard_'+p['operation'],'semantic_unit':p['effect_unit'],'kind':'effect','operation':p['operation']},{'action_id':p['compensation'],'semantic_unit':p['comp_unit'],'kind':'compensation'}]
        elif kind=='async_callback': actions += [{'action_id':p['callback_id'],'semantic_unit':p['callback_unit'],'kind':'callback'}]
    if case.family=='composite':
        for c in case.params['components']: comp(c['kind'],c['params'])
    else: comp(case.family,case.params)
    actions += [{'action_id':'finish','semantic_unit':'finish','kind':'finish'}]
    return CaseSpec(case.case_id,case.family,case.index,{'phase':'mid_execution'},[],actions,deps,[],{},[],'native_pause','target_resume',{'description':case.description})
