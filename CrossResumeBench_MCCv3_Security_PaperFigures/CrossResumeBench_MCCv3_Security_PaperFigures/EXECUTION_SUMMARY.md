# CrossResumeBench MCC v3 Security Stress + Paper Figures - Execution Summary

**Execution Date:** August 28, 2026  
**Status:** ✅ COMPLETED SUCCESSFULLY  
**Environment:** Windows, Python 3.12.4

---

## Overview

This package is the **final experimental and visualization stage** before architecture diagrams and paper drafting. It combines:

1. **Security Stress Testing** - Targeted attestation-integrity and trust-boundary stress tests
2. **Publication-Ready Figures** - 11 reproducible figures from validated holdout results
3. **Multi-Format Export** - Vector PDF/SVG + high-resolution PNG (600 DPI)
4. **Source Data Preservation** - Exact CSV data for each figure with suggested captions

**Critical:** This does NOT modify MCC v3, the sealed holdout, or post-validation statistics. It analyzes frozen, validated evidence.

---

## Execution Steps Completed

### 1. Environment Setup ✅
- Created new virtual environment: `.venv`
- Upgraded pip to 26.2.1
- Installed packages: pandas, numpy, matplotlib, jsonschema, pytest

### 2. Input Verification ✅
**Output:** `INPUT FREEZE PASS (15 files)`

Verified SHA-256 checksums for:
- 7 passed MCC v3 holdout result files
- 8 post-validation study result files

All inputs from validated experiments confirmed immutable and intact.

### 3. Security Stress Test Execution ✅

**Command:** `studies/security/run_security_stress.py`

**Test Design:**
- **768 total rows** (16 proof scenarios × 6 runtime pairs × 8 attack variants)
- **8 attack variants:**
  - 6 **in-threat-model** integrity attacks
  - 2 **out-of-threat-model** boundary cases

**Results:**
```json
{
  "safe_completion": 96,
  "safe_rejection": 480,
  "unsafe": 192,
  "in_model_integrity_gate_pass": true,
  "trust_boundary_exposed": true
}
```

### 4. Paper Figures Generation ✅

**Command:** `figures/scripts/generate_paper_figures.py`

**Generated:** 11 publication-ready figures × 3 formats = **33 files**

| Figure | Title | PDF | SVG | PNG | Data CSV |
|--------|-------|-----|-----|-----|----------|
| Fig 01 | Core Mechanism | ✅ | ✅ | ✅ | N/A (conceptual) |
| Fig 02 | Unsafe Rate Methods | ✅ | ✅ | ✅ | ✅ |
| Fig 03 | v2→v3 Transition | ✅ | ✅ | ✅ | ✅ |
| Fig 04 | Ablation Core Mechanism | ✅ | ✅ | ✅ | ✅ |
| Fig 05 | Statistical Safety Forest Plot | ✅ | ✅ | ✅ | ✅ |
| Fig 06 | Evidence Behavior | ✅ | ✅ | ✅ | ✅ |
| Fig 07 | Family Behavior | ✅ | ✅ | ✅ | ✅ |
| Fig 08 | Latency Overhead | ✅ | ✅ | ✅ | ✅ |
| Fig 09 | Payload Overhead | ✅ | ✅ | ✅ | ✅ |
| Fig 10 | Framework Pair Invariance | ✅ | ✅ | ✅ | ✅ |
| Fig 11 | Security Trust Boundary | ✅ | ✅ | ✅ | ✅ |

### 5. Output Verification ✅

**All Checks Passed:**
```json
{
  "rows_768": true,
  "no_technical_column_needed": true,
  "valid_controls_96_complete": true,
  "in_model_zero_unsafe": true,
  "in_model_mutations_reject_480": true,
  "trust_boundary_exposed": true,
  "paper_png_11": true,
  "paper_pdf_11": true,
  "paper_svg_11": true
}
```

### 6. Results Export ✅
**Generated:** `CrossResumeBench_MCCv3_Security_PaperFigures_results.zip`

Contains:
- Security stress test results and report
- All 33 figure files (11 × 3 formats)
- 10 source data CSVs
- Verification records

---

## Security Stress Test Findings

### Threat Model Scope

**MCC v3's Current Model:**
- **Trusted-witness hash attestation** for evidence integrity
- Detects unauthorized data mutation (value, subject, evidence tampering)
- Rejects conflicting certificates
- **Does NOT** authenticate issuer authority or bind certificates to unique contexts

### Test Results by Attack Class

#### A. In-Threat-Model Integrity Attacks (576 rows)

| Attack Variant | Expected Behavior | Actual Result | Pass/Fail |
|----------------|------------------|---------------|-----------|
| Valid control | Safe completion | 96 safe ✅ | ✅ PASS |
| Value tamper (no rehash) | Safe rejection | 96 reject ✅ | ✅ PASS |
| Subject tamper (no rehash) | Safe rejection | 96 reject ✅ | ✅ PASS |
| Evidence tamper (no rehash) | Safe rejection | 96 reject ✅ | ✅ PASS |
| Contract hash tamper | Safe rejection | 96 reject ✅ | ✅ PASS |
| Conflicting valid certificates | Safe rejection | 96 reject ✅ | ✅ PASS |

**In-Model Verdict:** ✅ **PASS** (0 unsafe, 480 correctly rejected, 96 valid completed)

#### B. Out-of-Threat-Model Boundary Cases (192 rows)

| Attack Variant | Expected Behavior | Actual Result | Interpretation |
|----------------|------------------|---------------|----------------|
| Cross-context replay | Exposes boundary | 96 unsafe ⚠️ | As expected - context binding not in model |
| Forged rehash (wrong value) | Exposes boundary | 96 unsafe ⚠️ | As expected - issuer auth not in model |

**Boundary Verdict:** ⚠️ **TRUST BOUNDARY EXPOSED** (as expected and documented)

### Security Interpretation

**What MCC v3 DOES guarantee:**
- Hash integrity detects all non-rehashed data mutations
- Rejects tampered evidence without explicit rehashing
- Blocks conflicting valid certificates for the same subject
- 0% unsafe rate for all in-threat-model integrity attacks

**What MCC v3 does NOT guarantee:**
- Certificate binding to unique case/context (replay attacks succeed)
- Issuer authority authentication (forged valid hashes succeed)
- Cryptographic security beyond trusted-witness attestation

**Claim Boundary:**
> "Hash integrity detects non-rehashed mutation, but does not authenticate issuer authority or bind certificates to a unique case/context. Out-of-model forged/replayed valid hashes are expected to expose this boundary."

**Honest disclosure:** The 192 out-of-model unsafe outcomes are **not failures** but **explicit boundary documentation**. They define what MCC v3 does NOT claim to protect against.

---

## Publication Figure Recommendations

### Strongest 5 Figures for Main Paper

1. **Figure 1 — Core Mechanism** 🌟
   - Conceptual diagram: MCC v2 failure vs MCC v3 closed-world rule
   - Perfect for introduction/motivation section

2. **Figure 3 — v2→v3 Transition** 🌟
   - Visual proof: all 294 unsafe v2 cases resolved by v3
   - Compelling before/after narrative

3. **Figure 4 — Ablation Study** 🌟
   - Shows removing closed-world gate → 174 unsafe cases return
   - Demonstrates component criticality

4. **Figure 5 — Statistical Forest Plot** 🌟
   - Base-case bootstrap safety effect with 95% confidence intervals
   - Rigorous quantitative evidence across all comparisons

5. **Figure 2 — Method Safety Comparison** 🌟
   - 0% MCC v3 unsafe vs 30-48% in non-privileged references
   - Clear, simple, high-impact summary graphic

### Supplementary/Results Section Figures

- **Figure 6** — Evidence-condition behavior breakdown
- **Figure 7** — Framework family behavior analysis
- **Figure 10** — Six runtime-pair invariance demonstration
- **Figure 8** — Mechanism latency overhead characterization
- **Figure 9** — Payload size overhead analysis

### Security/Limitations Section Figure

- **Figure 11** — Trusted-witness security boundary visualization
  - Shows in-model vs out-of-model attack outcomes
  - Critical for honest boundary disclosure

---

## Scientific Separation Maintained

| Component | Status | Source |
|-----------|--------|--------|
| MCC v3 mechanism | ❄️ FROZEN | Copied from validated package |
| 32-case holdout | ❄️ FROZEN | Passed June 2026, immutable |
| Post-validation results | ❄️ FROZEN | Completed statistics/ablation |
| Security stress test | 🆕 NEW | 768 rows, mechanism-level only |
| Paper figures | 🆕 NEW | Generated from frozen + security data |

**No retroactive modification** of validated experiments. Security study adds targeted integrity testing; figures visualize completed evidence.

---

## Generated File Inventory

### Security Results
- `results/security/SECURITY_VERDICT.json` - Structured security test outcomes
- `results/security/SECURITY_REPORT.md` - Human-readable security analysis
- `results/security/security_runs.csv` - Raw 768-row security stress data

### Paper Figures (11 figures × 3 formats)

**Vector Formats (publication-ready):**
- 11 × PDF files (for LaTeX/Overleaf)
- 11 × SVG files (for web/editing)

**Raster Format (high-resolution):**
- 11 × PNG files (600 DPI, for Word/PowerPoint)

**Source Data:**
- 10 × CSV files with exact data underlying each figure
- Enables independent reproduction and verification

### Verification & Export
- `results/VERIFICATION.json` - All output checks confirmed
- `CrossResumeBench_MCCv3_Security_PaperFigures_results.zip` - Complete archive

---

## Key Scientific Claims Supported

### 1. Safety Evidence (from frozen holdout)
- ✅ MCC v3: 0% unsafe (0/768 rows)
- ✅ Statistical significance: p < 0.001 across all comparisons
- ✅ Effect size: 30-48 percentage point unsafe-rate reduction
- ✅ 95% confidence intervals exclude zero

### 2. Component Importance (from frozen ablation)
- ✅ Closed-world gate is safety-critical (0% → 22.7% unsafe when removed)
- ✅ Other components affect efficiency, not fundamental safety
- ✅ History and certificates are complementary

### 3. Integrity Defense (NEW from security stress)
- ✅ 100% detection of non-rehashed data mutations (480/480)
- ✅ Valid controls complete safely (96/96)
- ✅ Zero in-threat-model failures (0/576 rows)

### 4. Trust Boundary Transparency (NEW)
- ⚠️ Context replay succeeds (96/96 as expected)
- ⚠️ Forged valid hashes succeed (96/96 as expected)
- ✅ Honest disclosure: 192/192 out-of-model cases expose documented limits

### 5. Performance Characterization (from frozen microbench)
- ✅ Median overhead: ~1.35 ms (vs 1.07 ms MCC v2)
- ✅ Payload: ~1 KB (vs 483 bytes MCC v2)
- ✅ Overhead acceptable for safety guarantees

---

## Research Protocol Compliance

✅ **Input freeze verification:** All 15 input files SHA-256 verified before use  
✅ **No retroactive modification:** Frozen holdout/post-validation untouched  
✅ **Security scope separation:** New 768-row study clearly marked as mechanism-level  
✅ **Honest boundary disclosure:** Out-of-model results included and explained  
✅ **Reproducible figures:** All figures generated from verifiable source data  
✅ **Multi-format export:** PDF/SVG (vector) + PNG (600 DPI raster)  
✅ **Source data preservation:** 10 CSV files enable independent verification  
✅ **Output verification:** All 9 verification checks passed  

---

## What This Package Enables

### For Paper Writing
- 11 publication-ready figures in multiple formats
- Suggested 5-figure main selection + 6 supplementary
- Source data CSVs for methods/reproducibility section
- Security boundary figure for limitations/discussion

### For Peer Review
- Complete security stress test results
- Transparent boundary documentation
- Independent figure data for verification
- Multi-format compatibility (LaTeX, Word, web)

### For Archival Record
- SHA-256 verified input provenance
- Complete audit trail from holdout → post-validation → security → figures
- Structured JSON verdicts + human-readable reports
- Single-ZIP export of all evidence

---

## Execution Timeline

1. Input verification: **< 1 second**
2. Security stress test: **< 2 minutes** (768 proof-layer scenarios)
3. Figure generation: **< 1 minute** (11 figures × 3 formats)
4. Output verification: **< 1 second**
5. Results export: **< 5 seconds**

**Total execution time: < 5 minutes**

---

## Next Steps for Publication

### Recommended Figure Selection
Use **5 main figures** (Fig 1, 2, 3, 4, 5) in paper body for professional presentation, with remaining 6 as supplementary material.

### Required Paper Sections

**Methods:**
- Reference frozen holdout SHA-256 checksums
- Cite 10,000 bootstrap replicates, case-level clustering
- Document 768-row security stress design

**Results:**
- Present statistical forest plot (Fig 5) as primary evidence
- Show v2→v3 transition (Fig 3) for visual impact
- Report ablation (Fig 4) for mechanism understanding

**Security/Limitations:**
- Include trust boundary figure (Fig 11)
- Explicitly state: "trusted-witness model, not cryptographic security"
- Acknowledge: "context binding and issuer authentication are out of scope"

**Reproducibility:**
- All figure source data included as CSV files
- SHA-256 input verification enables independent replication
- Code/data available in results ZIP

### Suggested Captions
Each figure's source data CSV includes suggested caption text. Review `docs/PAPER_FIGURE_SELECTION.md` for detailed guidance.

---

## Conclusion

The CrossResumeBench MCC v3 Security & Paper Figures package completed successfully, delivering:

1. **Validated security evidence:** 100% in-threat-model integrity defense (576/576 rows)
2. **Honest boundary disclosure:** 192/192 out-of-model attacks expose documented limits
3. **Publication-ready figures:** 11 figures × 3 formats = 33 high-quality outputs
4. **Complete reproducibility:** 10 source data CSVs + SHA-256 verified inputs
5. **Professional presentation:** Recommended 5-figure main selection identified

**The research package is publication-ready with full provenance, honest security boundaries, and reproducible visualization.**

---

**Archive Location:** `CrossResumeBench_MCCv3_Security_PaperFigures_results.zip`

**Generated Files:**
- 1 security verdict (JSON)
- 1 security report (Markdown)
- 1 security data (CSV, 768 rows)
- 11 figures × 3 formats (33 files)
- 10 figure source data CSVs
- 1 verification record (JSON)

**Total Package:** 47 output files + complete provenance chain

---

**Generated by:** Automated execution on Windows with Python 3.12.4  
**Execution Date:** August 28, 2026  
**Status:** ✅ READY FOR PAPER DRAFT
