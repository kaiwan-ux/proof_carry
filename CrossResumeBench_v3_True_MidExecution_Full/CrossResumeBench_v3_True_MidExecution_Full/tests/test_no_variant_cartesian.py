from crossresumebench_v3_full.cases import CASES
def test_ambiguity_only_where_meaningful():
    for c in CASES:
        if "ambiguous_external_commit" in c.applicable_variants: assert c.family in {"effect_commitment","compensation_pending"}
        if "missing_semantic_completion" in c.applicable_variants: assert c.family=="parallel_join"
