# CrossResumeBench MCC v3 Post-Validation Studies - Execution Summary

**Execution Date:** August 28, 2026  
**Status:** ✅ COMPLETED SUCCESSFULLY  
**Environment:** Windows, Python 3.12.4

---

## Overview

This post-validation study package analyzes the already-passed MCC v3 holdout (32 cases, 6,144 rows) through three complementary studies:

1. **Paired Statistical Validation** - Quantitative comparison against baselines
2. **Component Ablation Study** - Explanatory analysis of MCC v3 components
3. **Performance Microbenchmark** - Mechanism overhead measurement

---

## Execution Steps Completed

### 1. Environment Setup ✅
- Virtual environment: `.venv` (already configured)
- All dependencies installed successfully
- Python packages: langgraph, crewai, pandas, numpy, scipy, matplotlib, etc.

### 2. Input Verification ✅
```json
{
  "verified": true,
  "file_count": 7,
  "verdict_gate": true
}
```
- All 7 passed holdout files verified via SHA-256 checksums
- Research verdict gate confirmed as PASS

### 3. Post-Validation Study Execution ✅

**Command:** `python scripts/run_postvalidation.py --bootstrap-reps 10000 --micro-repeats 10`

**Results:**
```json
{
  "statistics": {
    "rows": 6144,
    "cases": 32,
    "comparisons": 5
  },
  "ablation": {
    "rows": 5376,
    "ablations": 7,
    "base_mcc_rows": 768
  },
  "performance_micro": {
    "instances": 768,
    "repeats": 10
  }
}
```

### 4. Results Verification ✅
**Output:** `POSTVALIDATION VERIFY PASS`

### 5. Results Export ✅
**Generated:** `CrossResumeBench_MCCv3_PostValidation_results.zip`

---

## Key Findings

### A. Statistical Validation Results

**MCC v3 Holdout Performance:**
- **Safe Completion Rate:** 486/768 (63.28%)
- **Unsafe Rate:** 0/768 (0.00%)
- **Wilson 95% CI for Unsafe Rate:** 0.000% to 0.498%

**Paired Comparisons (vs MCC v3):**

| Comparator | Unsafe Rate Reduction | 95% CI | p-value | Safe Completion Gain |
|------------|----------------------|---------|---------|---------------------|
| mcc_v2_frozen | -38.28 pp | -50.78 to -26.56 pp | 6.88e-05 | +8.59 pp |
| history_inference | -47.66 pp | -60.94 to -34.38 pp | 6.88e-05 | +10.94 pp |
| aaif_reference | -30.47 pp | -42.97 to -18.75 pp | 1.61e-04 | +25.00 pp |
| caplease_reference | -39.84 pp | -52.34 to -28.12 pp | 6.88e-05 | +3.12 pp |
| aaif_plus_caplease | -39.84 pp | -52.34 to -28.12 pp | 6.88e-05 | +3.12 pp |

**Statistical Method:**
- Primary clustering unit: base case (n=32), not individual rows
- Case-block bootstrap with 10,000 replicates
- Case-level Wilcoxon tests with Holm-Bonferroni adjustment
- All comparisons show statistically significant unsafe-rate reduction

### B. Component Ablation Analysis

**Purpose:** Explanatory post-validation analysis (NOT independent validation)

| Ablation Configuration | Safe Completion | Safe Rejection | Unsafe | Total Rows |
|------------------------|----------------|----------------|---------|------------|
| **full_mcc_v3** | **486** | **282** | **0** | **768** |
| minus_closed_world_gate | 540 | 54 | **174** | 768 |
| minus_integrity_verification | 540 | 228 | 0 | 768 |
| minus_identity_binding | 414 | 354 | 0 | 768 |
| minus_complete_snapshots | 366 | 402 | 0 | 768 |
| history_only | 126 | 642 | 0 | 768 |
| certificates_only | 342 | 426 | 0 | 768 |

**Key Insight:** Removing the closed-world gate introduces 174 unsafe outcomes, demonstrating its critical role in safety. Other components affect the completion/rejection balance but maintain safety.

### C. Performance Microbenchmark

**Mechanism Overhead (768 instances × 10 repeats):**

| Stage | Median | p95 | Mean |
|-------|--------|-----|------|
| mcc_v3_build | 642.60 µs | 3,078.40 µs | 988.57 µs |
| mcc_v3_resolve | 661.85 µs | 3,377.50 µs | 1,082.27 µs |
| mcc_v3_lower_total | 1,347.30 µs | 5,576.10 µs | 2,077.90 µs |
| mcc_v2_total | 1,066.70 µs | 4,831.10 µs | 1,720.66 µs |

**Payload Size:**
- MCC v3 median: 1,004 bytes
- MCC v2 median: 483 bytes
- Overhead: ~2.08× payload size, ~1.26× processing time

**Note:** Timing excludes native runtime scheduling/network/tool latency.

---

## Generated Outputs

### Statistics Results
- `case_level_rates.csv` - Per-case safety/completion rates
- `mccv3_by_evidence.csv` - Results grouped by evidence type
- `mccv3_by_family.csv` - Results grouped by agent framework family
- `method_summary.csv` - Summary across all methods
- `paired_comparisons.json` - Detailed statistical test results
- `STATISTICAL_REPORT.md` - Comprehensive statistical analysis

### Ablation Results
- `ablation_by_evidence.csv` - Ablation results by evidence type
- `ablation_by_family.csv` - Ablation results by framework family
- `ablation_runs.csv` - Raw ablation run data
- `ablation_summary.csv` - Ablation summary table
- `ABLATION_REPORT.md` - Detailed ablation analysis

### Performance Results
- `microbench.json` - Raw microbenchmark timing data
- `MICROBENCH_REPORT.md` - Performance analysis report

### Summary Files
- `POSTVALIDATION_SUMMARY.json` - High-level execution summary
- `CrossResumeBench_MCCv3_PostValidation_results.zip` - Complete results archive

---

## Interpretation Guidelines

### What These Results Support

1. **Paired Statistical Evidence:** MCC v3 shows statistically significant unsafe-rate reduction across all comparisons on this 32-case benchmark
2. **Component Importance:** The closed-world gate is critical for safety; other components affect efficiency
3. **Performance Characterization:** MCC v3 adds ~350 µs median overhead and ~500 bytes payload vs MCC v2

### Important Boundaries

1. **Generalization:** Statistical significance on this benchmark does not guarantee external generalization
2. **Ablation Scope:** Component analysis is explanatory, not confirmatory (holdout semantics already seen)
3. **Performance Context:** Overhead measurements are mechanism-only; end-to-end latency varies by runtime environment
4. **Comparison Scope:** AAIF/CapLease remain independent concept-level references, not claimed as universally inferior
5. **Security Model:** Current attestations use trusted-witness hashes, not cryptographic security guarantees

---

## Research Protocol Compliance

✅ **Input verification:** Passed holdout hashes and research gate verified  
✅ **Paired analysis:** Case-level clustering with block bootstrap (10,000 reps)  
✅ **Ablation isolation:** Separate study namespace, frozen mechanism untouched  
✅ **Performance methodology:** Warmup runs + repeated timings (10 repeats)  
✅ **Result preservation:** All raw outputs retained in results archive  
✅ **Attestation:** Input hash record included in export  

---

## Conclusion

The CrossResumeBench MCC v3 Post-Validation Studies completed successfully, providing:

- **Strong paired statistical evidence** for MCC v3's unsafe-rate reduction on this benchmark (0% unsafe vs 30-48% in comparators)
- **Component-level insights** showing the closed-world gate as safety-critical
- **Performance characterization** of ~1.3 ms median overhead and ~1 KB payload

All results are archived in `CrossResumeBench_MCCv3_PostValidation_results.zip` with full provenance and attestation records.

---

**Next Steps (Optional):**

To run the native end-to-end performance study:
```powershell
.\run_native_performance.ps1
```

Then re-export results:
```powershell
python scripts/export_results.py
```

---

**Generated by:** Automated execution on Windows with Python 3.12.4  
**Date:** August 28, 2026  
**Total Execution Time:** < 5 minutes
