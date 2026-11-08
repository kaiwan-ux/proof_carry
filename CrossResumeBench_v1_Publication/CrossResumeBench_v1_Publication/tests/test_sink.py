from pathlib import Path
import tempfile
from crossresumebench.services.sqlite_sink import SQLiteEffectSink,PostCommitTimeout
def test_post_commit_timeout_is_durable():
    p=Path(tempfile.mkdtemp())/'sink.db'; s=SQLiteEffectSink(p)
    try: s.execute('1','charge',post_commit_timeout=True)
    except PostCommitTimeout: pass
    assert s.count('charge')==1
    r=s.execute('1','charge'); assert r.deduplicated and s.count('charge')==1
