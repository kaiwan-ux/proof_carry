# MCC v3 Holdout Benchmark - Progress Monitor

## Benchmark Overview
- **Type**: MCC v3 Closed-World Holdout
- **Expected Probes**: 24 (8 families × 3 runtimes)
- **Expected Native Controls**: 96
- **Expected Native Sources**: 96
- **Expected Migrations**: 6,144 (128 case×variant × 6 pairs × 8 methods)

## Current Status
The benchmark is running in background process Terminal ID: 7

### Progress Tracking Commands

```powershell
# Check probe progress
Get-ChildItem results/probes/*.json -File -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count

# Check native controls
Get-ChildItem results/native_controls/*.json -File -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count

# Check native sources
Get-ChildItem results/native_sources/*.json -File -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count

# Check native targets (migrations)
Get-ChildItem results/native_targets/*.json -File -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count

# Check recent file activity
Get-ChildItem results -Recurse -File | Where-Object {$_.LastWriteTime -gt (Get-Date).AddMinutes(-5)} | Measure-Object | Select-Object -ExpandProperty Count

# Check work in progress
Get-ChildItem results/work -Directory -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
```

## Notes
- CrewAI shows interactive prompts that timeout after 20s - this is normal
- The benchmark will take considerable time (potentially hours) to complete all 6,144+ tests
- Files are written incrementally as tests complete
