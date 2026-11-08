import pandas as pd

print("=" * 60)
print("CrossResumeBench ProofCarry-104 Results Summary")
print("=" * 60)

# Semantic Study
df = pd.read_csv('results/semantic_runs.csv')
print("\n📊 SEMANTIC STUDY")
print(f"Total observations: {len(df):,}")
print(f"Base cases: {df['case_id'].nunique()}")
print(f"Methods tested: {df['method'].nunique()}")
print(f"Runtime pairs: {len(df[['source','target']].drop_duplicates())}")
print(f"\nOutcomes:")
print(f"  ✓ Safe completions: {df['safe_completion'].sum():,}")
print(f"  ✓ Safe rejections: {df['safe_rejection'].sum():,}")
print(f"  ✗ Unsafe violations: {df['unsafe_violation'].sum():,}")
print(f"  ⚠ Technical failures: {df['technical_failure'].sum():,}")

# Security Study  
df = pd.read_csv('results/security_runs.csv')
print("\n🔒 SECURITY STUDY")
print(f"Total observations: {len(df):,}")
print(f"Attack types: {df['attack'].nunique()}")
print(f"Methods: {df['method'].nunique()}")
safe = (df['expected'] == df['outcome']).sum()
unsafe = (df['expected'] != df['outcome']).sum()
print(f"\nOutcomes:")
print(f"  ✓ Expected behavior: {safe:,}")
print(f"  ✗ Unexpected behavior: {unsafe:,}")

# Ablation Study
df = pd.read_csv('results/ablation_runs.csv')
print("\n🔬 ABLATION STUDY")
print(f"Total observations: {len(df):,}")
print(f"Ablation configs: {df['ablation'].nunique()}")
print(f"Evidence conditions: {df['condition'].nunique()}")
print(f"\nOutcomes:")
print(f"  ✓ Safe completions: {df['safe_completion'].sum():,}")
print(f"  ✓ Safe rejections: {df['safe_rejection'].sum():,}")
print(f"  ✗ Unsafe outcomes: {df['unsafe'].sum():,}")

# Native Gate
df = pd.read_csv('results/native_family_gate.csv')
print("\n🔌 NATIVE FRAMEWORK GATE")
print(f"Framework probes: {len(df)}")
for fw in df['framework'].unique():
    passed = df[df['framework']==fw]['pass'].sum()
    total = len(df[df['framework']==fw])
    status = "✓" if passed == total else "✗"
    print(f"  {status} {fw}: {passed}/{total} passed")

print("\n" + "=" * 60)
print("OVERALL STATUS")
print("=" * 60)
print("✓ Semantic study: COMPLETE (31,200 rows)")
print("✓ Security study: COMPLETE (11,232 rows)")
print("✓ Ablation study: COMPLETE (17,472 rows)")
print("✗ Native study: TERMINATED (CrewAI lifecycle hang)")
print("✗ Performance study: NOT RUN (depends on native)")
print(f"\nTotal experimental observations: {31200 + 11232 + 17472:,}")
print("=" * 60)
