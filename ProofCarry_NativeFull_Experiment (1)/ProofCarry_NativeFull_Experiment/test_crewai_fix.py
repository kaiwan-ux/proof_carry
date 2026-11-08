#!/usr/bin/env python
"""Test CrewAI fix with a single family gate case."""
from __future__ import annotations
import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "frozen_v2" / "src")]

from crossresumebench_proofcarry.cases import CASE_BY_ID
from crossresumebench_proofcarry.native import get_runtime

def main():
    # Test with approval family (pc104-approval-01)
    case = CASE_BY_ID["pc104-approval-01"]
    runtime = get_runtime("crewai")
    run_dir = ROOT / "results" / "crewai_fix_test"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Testing CrewAI fix with case: {case.case_id}")
    print(f"Family: {case.family}")
    print(f"Run directory: {run_dir}")
    print()
    
    t0 = time.perf_counter()
    try:
        print("Running self_resume_case test...")
        result = runtime.self_resume_case(case, run_dir)
        elapsed = time.perf_counter() - t0
        
        print(f"\n✅ SUCCESS! Completed in {elapsed:.2f} seconds")
        print(f"Restore completed: {result.get('restore_completed')}")
        print(f"Safe: {result.get('safe')}")
        print(f"Resume API: {result.get('resume_api')}")
        
        if elapsed < 15:
            print(f"\n🎉 FIXED! Time is now {elapsed:.2f}s (was 55-80s before)")
            return 0
        else:
            print(f"\n⚠️  Still slow: {elapsed:.2f}s (expected <15s)")
            return 1
            
    except Exception as e:
        elapsed = time.perf_counter() - t0
        print(f"\n❌ FAILED after {elapsed:.2f} seconds")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
