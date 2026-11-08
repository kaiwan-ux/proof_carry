# Current Results Files - Location Guide

**Date**: 2026-08-27  
**Status**: Benchmark running - results accumulating in work directories

---

## Current Results Summary

**Total Files**: 29  
**Location**: `results/work/` (temporary work directories)

---

## Results by Type

### 1. CrewAI Probes (3 completed work directories)

**Location**: `results/work/probe-crewai-*/`

Each directory contains:
- `semantic_store.json` - The semantic state captured
- `checkpoints/main/*.json` - CrewAI checkpoint data
- `worker_config.json` - Worker configuration
- `worker_stdout.txt` - Standard output logs
- `worker_stderr.txt` - Error logs (if any)
- `source_ready.signal` - Signal file indicating source capture complete
- `stop.gate` - Gate file for synchronization

**Completed CrewAI Probes**:
1. `probe-crewai-crb-holdout-approval_wait-h01/`
   - Checkpoint: `20260827T170352_427be3d8_p-none.json`
   - 7 files total

2. `probe-crewai-crb-holdout-async_callback-h01/`
   - Checkpoint: `20260827T170424_0304ac84_p-none.json`
   - 7 files total

3. `probe-crewai-crb-holdout-compensation_pending-h01/`
   - Checkpoint: `20260827T170453_bfab6ac0_p-none.json`
   - 7 files total

### 2. LangGraph Probes (8 work directories)

**Location**: `results/work/probe-langgraph-*/`

Each directory contains:
- `semantic_store.json` - The semantic state captured

**LangGraph Probes Being Processed**:
1. `probe-langgraph-crb-holdout-approval_wait-h01/`
2. `probe-langgraph-crb-holdout-async_callback-h01/`
3. `probe-langgraph-crb-holdout-compensation_pending-h01/`
4. `probe-langgraph-crb-holdout-composite-h01/`
5. `probe-langgraph-crb-holdout-effect_commitment-h01/`
6. `probe-langgraph-crb-holdout-loop_pause-h01/`
7. `probe-langgraph-crb-holdout-parallel_join-h01/`
8. `probe-langgraph-crb-holdout-retry_pause-h01/`

---

## File Structure Details

### Typical CrewAI Probe Directory:
```
results/work/probe-crewai-crb-holdout-{family}-h01/
├── checkpoints/
│   └── main/
│       └── 20260827T{time}_{hash}_p-none.json    # CrewAI checkpoint
├── semantic_store.json                            # Semantic state
├── source_ready.signal                            # Ready signal
├── stop.gate                                      # Stop gate
├── worker_config.json                             # Configuration
├── worker_stderr.txt                              # Error logs
└── worker_stdout.txt                              # Output logs
```

### Typical LangGraph Probe Directory:
```
results/work/probe-langgraph-crb-holdout-{family}-h01/
└── semantic_store.json                            # Semantic state
```

---

## Expected Final Result Locations

When probes complete, results will be moved/written to:

### Probes (24 total expected):
```
results/probes/
├── probe-langgraph-crb-holdout-{family}-h01.json   # 8 families
├── probe-crewai-crb-holdout-{family}-h01.json      # 8 families  
└── probe-maf-crb-holdout-{family}-h01.json         # 8 families
```

### Native Controls (96 expected):
```
results/native_controls/
└── *.json                                          # One per test
```

### Native Sources (96 expected):
```
results/native_sources/
└── *.json                                          # One per test
```

### Migration Tests (6,144 expected):
```
results/native_targets/
└── *.json                                          # One per migration test
```

---

## How to Access Results

### View a Semantic Store:
```powershell
Get-Content results/work/probe-langgraph-crb-holdout-effect_commitment-h01/semantic_store.json | ConvertFrom-Json
```

### View CrewAI Checkpoint:
```powershell
Get-Content results/work/probe-crewai-crb-holdout-approval_wait-h01/checkpoints/main/20260827T170352_427be3d8_p-none.json | ConvertFrom-Json
```

### View Worker Output:
```powershell
Get-Content results/work/probe-crewai-crb-holdout-approval_wait-h01/worker_stdout.txt
```

### List All Completed Probes:
```powershell
Get-ChildItem results/work -Directory | Where-Object { Test-Path "$($_.FullName)/semantic_store.json" } | Select-Object Name
```

---

## Progress Tracking

### Current Status:
- **CrewAI Probes**: 3/8 work directories with full content
- **LangGraph Probes**: 8/8 work directories created (in progress)
- **MAF Probes**: 0/8 (not yet started)

### Check Completion:
```powershell
# Count work directories by framework
$lg = (Get-ChildItem results/work -Directory -Filter "probe-langgraph-*").Count
$crew = (Get-ChildItem results/work -Directory -Filter "probe-crewai-*").Count
$maf = (Get-ChildItem results/work -Directory -Filter "probe-maf-*").Count
Write-Host "LangGraph: $lg/8, CrewAI: $crew/8, MAF: $maf/8"
```

---

## Notes

1. **Work directories are temporary** - final results will be in `results/probes/*.json`
2. **Files accumulate incrementally** - the benchmark is still running
3. **CrewAI has more files** per probe due to checkpoint structure
4. **LangGraph is simpler** - mainly semantic stores
5. **Semantic stores are key** - they contain the observable state for verification

---

## When Results Are Complete

The runner will:
1. Process all work directories
2. Generate final JSON files in `results/probes/`, `results/native_controls/`, etc.
3. Run analysis: `scripts/analyze_results.py`
4. Verify integrity: `scripts/verify_results.py`
5. Export: `CrossResumeBench_MCCv3_Holdout_results.zip`

---

**Location**: `CrossResumeBench_MCCv3_ClosedWorld_Holdout/CrossResumeBench_MCCv3_ClosedWorld_Holdout/results/work/`
