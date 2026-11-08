"""Reserved for the later stochastic experiment. Not used in PCC v0 deterministic ablation."""
import os
if not os.getenv('GROQ_API_KEY'):
    print('LLM extension intentionally disabled. No API key is required for PCC v0 ablation.')
else:
    print('GROQ_API_KEY detected, but this script does not run during Phase-1. Keep LLM effects out of the deterministic ablation.')
