"""逐行落盘、关闭门和包结构的定向离线检查；不冒 PG 或原生树证明。"""
import asyncio
from contextlib import contextmanager
from datetime import datetime,timezone
import io
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from uuid import uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.data_exit.contracts import TABLES,PROFILE,Limits,DataError,canonical,digest
from app.data_exit.snapshot import SnapshotCoordinator
from app.data_exit.files import RootLease
from app.data_exit.spool import SpoolRows
from app.storage.originals import OriginalStore
from app.worker.gate import GateClosed
from app.worker.worker_main import run_controlled_worker


class Result:
    def __init__(self,value):self.value=value
    def fetchone(self):return self.value


class Cursor:
    def __init__(self,connection):self.connection=connection
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def execute(self,query):
        table=query.split('FROM public.')[1].split()[0]
        self.values=iter(self.connection.rows.get(table,()))
    def fetchmany(self,size):
        import itertools
        return list(itertools.islice(self.values,size))


class Connection:
    def __init__(self,rows,control):self.rows,self.control=rows,control
    def cursor(self,**kwargs):return Cursor(self)
    def execute(self,query):
        if 'FROM pg_roles' in query:return Result(dict(rolname='synthetic_snapshot',rolsuper=False,rolcreatedb=False,rolcreaterole=False,rolbypassrls=False))
        if 'CURRENT_TIMESTAMP' in query:return Result(dict(logical_time_utc=datetime.now(timezone.utc),database_snapshot='1:2:'))
        if 'data_export_control' in query:return Result(self.control)
        raise AssertionError(query)


class Incremental(unittest.TestCase):
    def test_disk_spool_exact_rows_and_limit(self):
        root=Path(os.environ['RETROLUME_TASK114_SCRATCH'])
        store=OriginalStore(root);raw='逐行保存\r\n原文保持。'.encode('utf-8')
        original=store.put(io.BytesIO(raw),max_bytes=4096)
        sid,vid=str(uuid4()),str(uuid4())
        rows={table:[] for table in TABLES}
        rows['material_sources']=[dict(id=sid,title='合成资料',current_version=vid,revision=1)]
        rows['material_versions']=[dict(id=vid,source_id=sid,filename='合成.md',format='md',sha256=original.sha256,size=len(raw),created_at=datetime.now(timezone.utc))]
        control=dict(dataset_id=str(uuid4()),schema_profile=PROFILE,created_at=datetime.now(timezone.utc),source_instance_observed=str(uuid4()),mode_observed='normal',source_snapshot_id=None,source_root_sha256=None)
        lock=RootLease(root)
        snapshot=SnapshotCoordinator('unused',store,lock,root)
        @contextmanager
        def connection(**kwargs):yield Connection(rows,control)
        snapshot.repository=SimpleNamespace(connection=connection)
        result=snapshot.capture(str(uuid4()),'restore_checkpoint',{'mode':'all'})
        self.assertIsInstance(result.rows['material_versions'],SpoolRows)
        self.assertEqual(len(result.rows['material_versions']),1)
        self.assertEqual((result.root/'texts'/f'{original.sha256}.txt').read_bytes(),raw)
        for table in TABLES:self.assertEqual((result.root/'records'/f'{table}.jsonl').read_bytes(),(result.root/'checkpoint'/f'{table}.jsonl').read_bytes())
        expected={'closure':result.scope,'materials':list(result.rows['material_sources']),'versions':list(result.rows['material_versions']),
                  'activity_scope_sources':[],'activity_memory_choices':[],'learning_memory_dependencies':[]}
        self.assertEqual(snapshot.closure_digest(result.rows,result.scope),digest(canonical(expected)))
        snapshot.limits=Limits(chunk_bytes=10)
        with self.assertRaises(DataError):snapshot.capture(str(uuid4()),'restore_checkpoint',{'mode':'all'})
        lock.close()

    def test_closing_gate_finishes_existing_call_and_rejects_late_call(self):
        async def scenario():
            state={'fence':None};closed=[]
            class Gateway:
                async def call(self,context,request):
                    await asyncio.sleep(.25)
                    return '已提交的原调用'
            async def work(gate):
                task=asyncio.create_task(gate.call(None,None))
                await asyncio.sleep(.02);state['fence']={'state':'draining'}
                await asyncio.sleep(.12)
                closed.append(gate.closed)
                with self.assertRaises(GateClosed):await gate.call(None,None)
                self.assertEqual(await task,'已提交的原调用')
            await run_controlled_worker(Gateway(),work,drain_timeout_seconds=1,
                maintenance_gate=SimpleNamespace(hub=SimpleNamespace(state=lambda:state)))
            self.assertEqual(closed,[True])
        asyncio.run(scenario())


if __name__=='__main__':unittest.main(verbosity=2)
