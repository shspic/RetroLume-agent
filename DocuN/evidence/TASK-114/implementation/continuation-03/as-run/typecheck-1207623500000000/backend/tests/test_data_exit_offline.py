"""离线核对字节锁、提交日志、选择围栏和非执行 codec；保留测试原件。"""
import io
import json
import os
from pathlib import Path
import struct
import sys
import threading
import unittest
from uuid import uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.data_exit.codec import load_json,encode_row,decode_row
from app.data_exit.contracts import DataContext,DataError,DataJobCommand,canonical
from app.data_exit.control import ControlHub,TAIL
from app.data_exit.files import RootLease
from app.data_exit.maintenance import MutationGate,sql_writes
from app.data_exit.packages import allowed_member


class DataExitOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('RETROLUME_TASK114_SCRATCH')
        if not value:raise RuntimeError('缺专用合成 scratch，不借用户目录')
        cls.root=Path(value)
        if not cls.root.is_dir():raise RuntimeError('scratch 必须已获准并存在')
        cls.hubroot=cls.root/'offline-control'
        cls.hubroot.mkdir()
        cls.hub=ControlHub(cls.hubroot)
        cls.context=DataContext(cls.hub.control_id,0,str(uuid4()),str(uuid4()),'normal')

    def test_01_shared_locks_and_exclusive_wait_across_threads(self):
        lock=RootLease(self.root)
        with lock.acquire():
            with lock.acquire():pass
            result=[]
            def attempt():
                try:
                    with lock.acquire(True,timeout=.05):result.append('entered')
                except DataError as error:result.append(error.code)
            thread=threading.Thread(target=attempt);thread.start();thread.join(1)
            self.assertFalse(thread.is_alive());self.assertEqual(result,['operation_timeout'])
        with lock.acquire(True,timeout=.05):pass
        lock.close()

    def test_02_key_replay_conflict_and_readonly_query(self):
        key=str(uuid4());command=DataJobCommand('portable_export',key,{'mode':'all'})
        first=self.hub.create_or_get_job(command,self.context)
        self.assertEqual(first['job_id'],self.hub.create_or_get_job(command,self.context)['job_id'])
        before=self.hub.path.read_bytes()
        self.assertEqual(self.hub.get_by_key(key)['job_id'],first['job_id'])
        self.hub.reconcile(first['job_id']);self.assertEqual(self.hub.path.read_bytes(),before)
        with self.assertRaises(DataError):self.hub.create_or_get_job(DataJobCommand('portable_export',key,{'mode':'selected'}),self.context)

    def test_03_json_duplicate_surrogate_depth_and_nan(self):
        for value in (b'{"x":1,"x":2}',b'{"x":NaN}',b'"\\ud800"',b'\xef\xbb\xbf{}',b'['*34+b'0'+b']'*34):
            with self.assertRaises(DataError):load_json(value)
        self.assertEqual(load_json(' {"text":"原文\\r\\n"} '),{'text':'原文\r\n'})

    def test_04_no_path_or_executable_entry(self):
        for name in ('../x','/x','C:/x','originals/../x','\\\\host\\x','records/x.sql','records/material_sources.jsonl:ads','README.txt/','originals/'+'f'*64+'.zip'):
            self.assertFalse(allowed_member(name),name)
        self.assertTrue(allowed_member('originals/'+'f'*64))
        self.assertTrue(allowed_member('records/material_sources.jsonl'))

    def test_05_sql_guard_does_not_treat_lock_as_update(self):
        self.assertFalse(sql_writes('SELECT id FROM activities FOR UPDATE'))
        self.assertFalse(sql_writes("SELECT 'DELETE FROM activities' AS note"))
        self.assertTrue(sql_writes('WITH q AS (DELETE FROM activities RETURNING id) SELECT * FROM q'))
        self.assertTrue(sql_writes('SELECT public.html_update_preview(%s,%s,%s,%s,%s,%s,%s)'))
        from psycopg import sql
        self.assertTrue(sql_writes(sql.SQL('INSERT INTO {} DEFAULT VALUES').format(sql.Identifier('activities'))))

    def test_06_control_cache_is_not_authority_and_fence_rejects_new_work(self):
        (self.hubroot/'state.json').write_text('{"mode":"normal","selection_generation":999}',encoding='utf-8')
        gate=MutationGate(self.hub,lambda:self.context)
        with gate.acquire() as permit:
            owned=gate.register_owned('offline',{'purpose':'有限收尾验证'})
            self.hub.commit('maintenance.fence',{'origin':self.context.public(),'state':'draining'})
            with self.assertRaises(DataError):permit.check(outgoing=True)
            with gate.close_lane(owned):permit.check()
            with self.assertRaises(DataError):gate.register_owned('offline',{})
        with self.assertRaises(DataError):
            with gate.acquire():pass
        gate.end_owned(owned,confirmed=True)

    def test_07_selector_commit_after_lost_response_has_same_generation(self):
        key=str(uuid4());job=self.hub.create_or_get_job(DataJobCommand('activate',key,{'expected_generation':0}),self.context)
        self.hub.commit('selector_commit',{'generation':1,'target_id':str(uuid4()),'dataset_id':str(uuid4()),'instance_id':str(uuid4()),
                                         'activation_job_id':job['job_id'],'mode':'restored_readonly'})
        before=self.hub.path.read_bytes()
        receipt=self.hub.get_by_key(key)
        self.assertEqual(receipt['selection_generation'],1);self.assertEqual(receipt['state'],'active_readonly')
        self.assertEqual(self.hub.path.read_bytes(),before)

    def test_08_partial_tail_reads_confirmed_prefix_and_blocks_mutation(self):
        before=self.hub.path.read_bytes()
        with self.hub.path.open('ab') as stream:stream.write(struct.pack('!I',100)+b'{"partial":')
        self.assertTrue(self.hub.state()['selection'])
        with self.assertRaises(DataError):self.hub.commit('unsafe',{})
        # 断尾作为失败原件保存；此后不继续向该日志追加。
        (self.root/'journal-prefix.bin').write_bytes(before)
        (self.root/'journal-tail.bin').write_bytes(self.hub.path.read_bytes())


if __name__=='__main__':unittest.main(verbosity=2)
