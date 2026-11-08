from __future__ import annotations
import sqlite3
from pathlib import Path
from dataclasses import dataclass

class PostCommitTimeout(RuntimeError): pass
class PreCommitFailure(RuntimeError): pass

@dataclass
class SinkResult:
    operation_id: str
    status: str
    deduplicated: bool

class SQLiteEffectSink:
    """Tiny durable external-effect service used by the benchmark.

    It is intentionally outside framework state. `post_commit_timeout=True` commits
    first and then loses the acknowledgement, creating the classic ambiguous-outcome case.
    """
    def __init__(self,path:Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute('create table if not exists effects(operation_id text primary key, op text, commits integer not null, idem_key text)')
    def execute(self,operation_id:str,op:str,*,idempotency_key:str|None=None,pre_commit_failure=False,post_commit_timeout=False)->SinkResult:
        if pre_commit_failure: raise PreCommitFailure(operation_id)
        with sqlite3.connect(self.path) as c:
            row=c.execute('select commits from effects where operation_id=?',(operation_id,)).fetchone()
            if row is not None:
                return SinkResult(operation_id,'committed',True)
            c.execute('insert into effects(operation_id,op,commits,idem_key) values(?,?,1,?)',(operation_id,op,idempotency_key)); c.commit()
        if post_commit_timeout: raise PostCommitTimeout(operation_id)
        return SinkResult(operation_id,'committed',False)
    def count(self,op:str)->int:
        with sqlite3.connect(self.path) as c:
            row=c.execute('select count(*) from effects where op=?',(op,)).fetchone(); return int(row[0])
    def ledger(self)->dict[str,int]:
        with sqlite3.connect(self.path) as c:
            return {op:int(n) for op,n in c.execute('select op,count(*) from effects group by op')}
