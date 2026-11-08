from crossresumebench.generator import generate_suite,FAMILIES
def test_suite_shape_and_unique_ids():
    c=generate_suite(); assert len(c)==60; assert len({x.case_id for x in c})==60; assert set(x.family for x in c)==set(FAMILIES)
def test_reference_terminates():
    for c in generate_suite(): assert c.reference_final_state['terminated'] is True
