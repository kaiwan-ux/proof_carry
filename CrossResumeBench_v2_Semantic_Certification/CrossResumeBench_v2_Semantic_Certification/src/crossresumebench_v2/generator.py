from __future__ import annotations
import random, hashlib
from .models import CaseSpec, ActionSpec

FAMILIES=[
 "effect_parent_completion_gap","parallel_branch_completion_gap","subworkflow_return_gap","atomic_to_expanded_posteffect",
 "expanded_to_atomic_posteffect","approval_after_effect_boundary","callback_closes_semantic_unit","compensation_scope_closure",
 "retry_effect_attempt_boundary","join_requires_certified_branch","loop_effect_iteration_boundary","conditional_effect_merge",
 "multi_effect_semantic_unit","pending_tool_then_semantic_close",
]
BOUNDARIES=["mid_node_interrupt","superstep_end","method_boundary","pending_request","tool_timeout","callback_wait","fanout_partial"]

def A(i,u,k="step",op=None,deps=None,parent=None,**m):
    return ActionSpec(i,u,k,op,deps or [],parent,m).to_dict()

def _plans(fam,v,rng):
    # Every family is new relative to CrossResumeBench v1 and mixes source/target granularity differently.
    # Five variants perturb labels, observability and boundary metadata without changing the semantic question.
    suff=f"_{v}"
    if fam=="effect_parent_completion_gap":
        src=[A("prepare","prepare"),A("charge_native","purchase","effect","charge",parent="purchase",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_effect=True,certify_completion=True)]
        tgt=[A("prepare_t","prepare"),A("authorize","purchase",completes_unit=False),A("charge_t","purchase","effect","charge",parent="purchase",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["effect-vs-parent-completion","one-to-many"]
    elif fam=="parallel_branch_completion_gap":
        src=[A("fanout","fanout"),A("a_effect","branch_a","effect","reserve_a",parent="branch_a",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True),A("b_start","branch_b",emit_completion=False,unit_completed=False)]
        tgt=[A("fanout_t","fanout"),A("a_t","branch_a","effect","reserve_a"),A("b_t","branch_b"),A("join","join","join",deps=["branch_a","branch_b"]),A("finish","finish","finish")]
        deps={"join":["branch_a","branch_b"]}; tags=["parallel-partial","semantic-branch-certificate"]
    elif fam=="subworkflow_return_gap":
        src=[A("enter","parent"),A("child_effect","child_work","effect","ticket",parent="child_work",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True),A("child_return","child_work",emit_completion=False,certify_completion=True)]
        tgt=[A("parent_t","parent"),A("child_combined","child_work",completes_unit=False),A("ticket_t","child_work","effect","ticket",completes_unit=True),A("after_child","after_child"),A("finish","finish","finish")]
        deps={}; tags=["subworkflow-return","nested-granularity"]
    elif fam=="atomic_to_expanded_posteffect":
        src=[A("source_atomic","checkout","effect","payment",parent="checkout",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True)]
        tgt=[A("auth","checkout",completes_unit=False),A("capture","checkout","effect","payment",completes_unit=False),A("receipt","checkout",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["atomic-to-expanded","post-effect-work"]
    elif fam=="expanded_to_atomic_posteffect":
        src=[A("auth_s","checkout",emit_completion=False,unit_completed=False),A("pay_s","checkout","effect","payment",parent="checkout",actual_commit=True,observed_commit="unknown",unit_completed=False,emit_completion=False,certify_effect=True),A("receipt_s","checkout",emit_completion=True,certify_completion=True)]
        tgt=[A("combined","checkout","effect","payment"),A("finish","finish","finish")]
        deps={}; tags=["expanded-to-atomic","semantic-aggregation"]
    elif fam=="approval_after_effect_boundary":
        src=[A("reserve","reservation","effect","reserve",parent="reservation",actual_commit=True,observed_commit="unknown",unit_completed=False,emit_completion=False),A("approval_req","approval","approval",request_id="approve",blocks="reservation",certify_obligation=True)]
        tgt=[A("reserve_t","reservation","effect","reserve",completes_unit=False),A("approval_t","reservation","approval",request_id="approve",completes_unit=False),A("confirm","reservation",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["effect-before-approval","pending-obligation"]
    elif fam=="callback_closes_semantic_unit":
        src=[A("submit","submission","effect","submit",parent="submission",actual_commit=True,observed_commit="unknown",unit_completed=False,emit_completion=False),A("callback_wait","submission","callback",op="submit",callback_id="cb")]
        tgt=[A("submit_t","submission","effect","submit",completes_unit=False),A("callback_t","submission","callback",op="submit",callback_id="cb",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["callback-completion","effect-not-unit-complete"]
    elif fam=="compensation_scope_closure":
        src=[A("debit","debit_scope","effect","debit",parent="debit_scope",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True),A("need_refund","refund","compensation",op="debit")]
        tgt=[A("debit_t","debit_scope","effect","debit"),A("refund_t","refund","compensation",op="debit"),A("finish","finish","finish")]
        deps={}; tags=["compensation","scope-closure"]
    elif fam=="retry_effect_attempt_boundary":
        src=[A("attempt1","remote_call","step",retry=(1,3),emit_completion=False,unit_completed=False),A("attempt2_effect","remote_call","effect","charge",parent="remote_call",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True)]
        tgt=[A("attempt_t","remote_call","effect","charge"),A("finish","finish","finish")]
        deps={}; tags=["retry-vs-effect","attempt-ownership"]
    elif fam=="join_requires_certified_branch":
        src=[A("a_done","a",emit_completion=True),A("b_effect","b","effect","bop",parent="b",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True)]
        tgt=[A("a_t","a"),A("b_t","b","effect","bop"),A("join","join","join",deps=["a","b"]),A("finish","finish","finish")]
        deps={"join":["a","b"]}; tags=["join","certified-branch"]
    elif fam=="loop_effect_iteration_boundary":
        src=[A("iter1","iteration_1",counter=("loop",1)),A("iter2_effect","iteration_2","effect","loop_write",parent="iteration_2",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True,counter=("loop",2))]
        tgt=[A("iter1_t","iteration_1"),A("iter2_t","iteration_2","effect","loop_write"),A("iter3","iteration_3"),A("finish","finish","finish")]
        deps={}; tags=["loop-position","effect-iteration"]
    elif fam=="conditional_effect_merge":
        src=[A("route","route",decision=("route","left")),A("left_effect","left_branch","effect","left_write",parent="left_branch",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True)]
        tgt=[A("route_t","route"),A("left_t","left_branch","effect","left_write"),A("merge","merge"),A("finish","finish","finish")]
        deps={}; tags=["conditional-merge","branch-completion"]
    elif fam=="multi_effect_semantic_unit":
        src=[A("e1","bundle","effect","e1",parent="bundle",actual_commit=True,observed_commit="committed",unit_completed=False,emit_completion=False),A("e2","bundle","effect","e2",parent="bundle",actual_commit=True,observed_commit="unknown",unit_completed=True,emit_completion=False,certify_completion=True)]
        tgt=[A("bundle_e1","bundle","effect","e1",completes_unit=False),A("bundle_e2","bundle","effect","e2",completes_unit=False),A("bundle_post","bundle",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["multi-effect-unit","mixed-observability"]
    elif fam=="pending_tool_then_semantic_close":
        src=[A("tool_send","tool_scope","effect","toolop",parent="tool_scope",actual_commit=True,observed_commit="unknown",unit_completed=False,emit_completion=False),A("callback","tool_scope","callback",op="toolop",callback_id="toolcb")]
        tgt=[A("tool_t","tool_scope","effect","toolop",completes_unit=False),A("callback_t","tool_scope","callback",op="toolop",callback_id="toolcb",completes_unit=False),A("post","tool_scope",completes_unit=True),A("finish","finish","finish")]
        deps={}; tags=["pending-tool","semantic-close"]
    else: raise KeyError(fam)
    return src,tgt,deps,tags

def make_case(family,variant,seed):
    rng=random.Random(seed+variant*10007+sum(map(ord,family)))
    cid=f"crb2-{family}-v{variant:02d}"
    src,tgt,deps,tags=_plans(family,variant,rng)
    # Meaningful hold-out variants (not pseudo-replications):
    # v1: certificates available for ambiguous facts; v2: semantic completion becomes history-observable;
    # v3: semantic-completion certificate withheld; v4: effect commit becomes history-observable and receipt is withheld;
    # v5: effect remains ambiguous and effect receipt is withheld.
    effect_seen=False
    for a in src:
        if a.get("kind") != "effect":
            continue
        m=a.setdefault("metadata",{}); effect_seen=True
        if variant==2 and m.get("unit_completed",True):
            m["emit_completion"]=True; m["certify_completion"]=False
        elif variant==3 and m.get("unit_completed",True):
            m["emit_completion"]=False; m["certify_completion"]=False
        elif variant==4:
            m["observed_commit"]="committed"; m["certify_effect"]=False
        elif variant==5:
            m["observed_commit"]="unknown"; m["certify_effect"]=False
    expected_units=[]; effects={}
    for a in tgt:
        u=a["semantic_unit"]
        if u not in expected_units: expected_units.append(u)
        if a.get("kind")=="effect" and a.get("operation"): effects[a["operation"]]=1
    # compensation effects are recorded separately but source effect remains exactly once.
    sb=BOUNDARIES[(variant+len(family))%len(BOUNDARIES)]; tb=BOUNDARIES[(variant*3+len(family))%len(BOUNDARIES)]
    return CaseSpec(cid,family,variant,{"variant":variant,"request_id":cid,"amount":100+variant},src,tgt,deps,expected_units,effects,tags+[f"source:{sb}",f"target:{tb}"],sb,tb,{"seed":seed,"suite":"v2-independent-holdout","mechanism_frozen_before_suite":True})

def generate_suite(seed=26082701,variants_per_family=5):
    return [make_case(f,v,seed) for f in FAMILIES for v in range(1,variants_per_family+1)]

def suite_hash(cases):
    import json
    return hashlib.sha256(json.dumps([c.to_dict() for c in cases],sort_keys=True,separators=(",",":")).encode()).hexdigest()
