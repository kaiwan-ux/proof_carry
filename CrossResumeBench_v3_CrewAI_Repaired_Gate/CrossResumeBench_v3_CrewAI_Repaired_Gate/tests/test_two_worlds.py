
from crossresumebench_crewai_gate.models import NativePause
from crossresumebench_crewai_gate.evidence import source_capture_from_native
from crossresumebench_crewai_gate.case import case_spec,spec_hash
from crossresumebench_crewai_gate.frozen import build_mcc_v2,reconstruct_mcc_v2,admissibility,ROOT

def n(world):
    count=1 if world=="committed" else 0
    return NativePause("crewai","effect_commit_two_worlds",f"cp-{world}","fake",["ack"],{"phase":"effect_attempted"},{"framework":"crewai"},{"effect_count":count,"ack_count":0,"finish_count":0},world)

def test_ambiguous_payloads_identical_and_reject():
    pa=build_mcc_v2(source_capture_from_native(n("committed"),"ambiguous_external_commit"),"crewai",spec_hash(),ROOT/"frozen_v2")
    pb=build_mcc_v2(source_capture_from_native(n("not_committed"),"ambiguous_external_commit"),"crewai",spec_hash(),ROOT/"frozen_v2")
    assert pa.payload==pb.payload
    rc,_=reconstruct_mcc_v2(pa.payload,case_spec(),ROOT/"frozen_v2")
    ok,reason=admissibility(rc)
    assert not ok and "AMBIGUOUS_EXTERNAL_COMMIT" in reason

def test_enough_evidence_disambiguates_both_worlds():
    for world in ["committed","not_committed"]:
        p=build_mcc_v2(source_capture_from_native(n(world),"enough_evidence"),"crewai",spec_hash(),ROOT/"frozen_v2")
        rc,_=reconstruct_mcc_v2(p.payload,case_spec(),ROOT/"frozen_v2")
        ok,_=admissibility(rc)
        assert ok and rc.effect_facts["effect"]["status"]==world
