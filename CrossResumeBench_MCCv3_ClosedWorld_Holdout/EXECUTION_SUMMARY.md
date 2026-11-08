# MCC v3 Holdout Benchmark - Execution Summary

**Date**: 2026-08-27  
**Status**: 🔄 **RESTARTED - RUNNING**

---

## ❌ Previous Attempt

The first execution attempt (Terminal ID 7) encountered issues:
- Process got stuck on CrewAI interactive prompts
- Prompts appeared repeatedly asking to view execution traces
- Despite environment variables set to disable tracing, prompts continued
- Process manually stopped after no progress for extended period
- **11 probe work directories** were created (3 CrewAI + 8 LangGraph)
- **29 work files** remained in `results/work/`
- **0 final results** were written to results directories

---

## 🔄 Current Attempt  

**Process ID**: Terminal 3 (background)  
**Started**: Just now  
**Environment**: All CrewAI telemetry/tracing disabled

### Expected Progress Sequence:
1. **Native Family Probes** (24 total)
   - 8 families × 3 runtimes (LangGraph, CrewAI, MAF)
   - ~20-40 minutes

2. **Native Controls** (96 total)
   - Self-resume tests for each framework
   - ~30 minutes

3. **Native Sources** (96 total)
   - Source capture tests
   - ~30 minutes

4. **Migrations** (6,144 total)
   - 128 case×variant × 6 pairs × 8 methods
   - ~2-3 hours

---

## 📊 Target Counts

| Category | Expected |
|----------|----------|
| Probes | 24 |
| Native Controls | 96 |
| Native Sources | 96 |
| Migrations | 6,144 |
| **TOTAL** | **6,360** |

---

## 🎯 Success Criteria

For MCC v3 to be considered successful:
- ✅ **0 unsafe continuations** (vs MCC v2's 40%)
- ✅ **0 technical failures**
- ✅ **96/96 native tests passing**
- ✅ **All preregistered expectations matched**

---

## 📁 Results Location

### Current State (Work in Progress):
```
results/work/
└── [probe directories with intermediate files]
```

### Final Results (When Complete):
```
results/
├── probes/              # 24 probe JSON files
├── native_controls/     # 96 control test JSON files
├── native_sources/      # 96 source capture JSON files
└── native_targets/      # 6,144 migration test JSON files
```

---

## 🔍 Monitoring Commands

```powershell
# Quick status
cd CrossResumeBench_MCCv3_ClosedWorld_Holdout/CrossResumeBench_MCCv3_ClosedWorld_Holdout

Write-Host "Probes: $((Get-ChildItem results/probes -File -EA SilentlyContinue).Count)/24"
Write-Host "Controls: $((Get-ChildItem results/native_controls -File -EA SilentlyContinue).Count)/96"
Write-Host "Sources: $((Get-ChildItem results/native_sources -File -EA SilentlyContinue).Count)/96"
Write-Host "Migrations: $((Get-ChildItem results/native_targets -File -EA SilentlyContinue).Count)/6144"

# Check recent activity
$recent = Get-ChildItem results -Recurse -File | Where-Object {$_.LastWriteTime -gt (Get-Date).AddMinutes(-5)}
Write-Host "Files modified in last 5 min: $($recent.Count)"
```

---

## ⏱️ Estimated Timeline

- **Total Duration**: 3-4 hours
- **Current Phase**: Native probes (just started)
- **Check Back**: Every 30-60 minutes

---

## 📝 Notes

### Known Issues from Previous Run:
1. CrewAI interactive prompts appear even with tracing disabled
2. Prompts timeout after 20s and should allow continuation
3. Process may appear stuck but could be processing in background

### Mitigation Strategy:
- Running in background (non-blocking)
- Will monitor file creation to track real progress
- Process will run to completion or error

---

## 🎓 Research Context

This benchmark tests whether **MCC v3's proof-obligation approach** can achieve 0% unsafe continuations where **MCC v2 had 40%** unsafe rates.

**MCC v3 Innovation**: Closed-world proof obligations
- Target declares continuation-critical facts
- Every fact must be proven from history/attestations/snapshots
- Missing or conflicting facts = REJECTION
- No more "missing evidence => no obligation" unsafe behavior

**Holdout Integrity**:
- MCC v3 mechanism frozen BEFORE holdout generation
- 32 fresh cases never seen during development
- Scientific separation maintained

---

**Status**: Execution restarted and running autonomously in background (Terminal 3)
