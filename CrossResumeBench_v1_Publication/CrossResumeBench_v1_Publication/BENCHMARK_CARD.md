# CrossResumeBench v1 benchmark card
**Purpose:** stress-test cross-runtime continuation semantics, not LLM quality.  
**Cases:** 60 generated hold-out semantic cases from 12 new families, five variants each.  
**Native confirmation:** one frozen variant/family across all six directed pairs of LangGraph, CrewAI and MAF.  
**No LLM:** deterministic by design.  
**External effects:** represented by a durable ledger model; `SQLiteEffectSink` is included for later fault-injection expansion.  
**Known limitation:** native adapters execute a normalized continuation inside the target runtime rather than directly translating proprietary checkpoint bytes.  
**Reproducibility:** mechanism hash, suite hash, environment capture, raw per-run artifacts, checksums and manifest.
