"""真实文件锁内校验当前字节，缓存不能隐藏修订、取消和损坏。"""
from pathlib import Path
from tempfile import mkdtemp
import os
import time
import unittest
from uuid import uuid4
from app.data_exit.control import ControlHub
from app.data_exit.contracts import DataContext, DataJobCommand, DataError
from app.data_exit.operations import Operation, request_cancel


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(mkdtemp(prefix='retrolume-snapshot-check-',dir=os.environ.get('S08_EVIDENCE')))
        self.hub = ControlHub(self.root)
        context = DataContext(self.hub.control_id, 0, str(uuid4()), str(uuid4()), 'normal')
        self.job = self.hub.create_or_get_job(DataJobCommand('restore', str(uuid4()), {'plan_id':str(uuid4()), 'plan_sha256':'0'*64}), context)
        self.op = Operation(self.hub, self.job['job_id'], 60, 'snapshot-test')
        self.op.check()

    def tearDown(self):
        self.hub.lock.close(); self.hub.operation_lock.close()

    def test_returned_state_is_detached_and_peer_cancel_is_current(self):
        value = self.hub.state()
        value['jobs'][self.job['job_id']]['state'] = 'failed'
        self.op.check()
        peer = ControlHub(self.root)
        try:
            request_cancel(peer, self.job['job_id'])
            with self.assertRaises(DataError) as caught: self.op.check()
            self.assertEqual(caught.exception.code, 'operation_cancelled')
        finally: peer.lock.close(); peer.operation_lock.close()

    def test_same_size_same_mtime_tamper_is_rejected(self):
        path = self.hub.path; info = path.stat(); raw = bytearray(path.read_bytes())
        raw[40] ^= 1; path.write_bytes(raw); os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        with self.assertRaises(DataError): self.op.check()

    def test_truncation_cannot_keep_old_execution(self):
        self.hub.path.write_bytes(b'')
        with self.assertRaises((DataError, KeyError)): self.op.check()

    def test_new_revision_and_clock_authority_still_fail_closed(self):
        self.hub.change_job(self.job['job_id'], lambda j: {'stage': 'peer-revised'})
        with self.assertRaises(DataError) as caught: self.op.check()
        self.assertEqual(caught.exception.code, 'request_conflict')
        self.hub.change_job(self.job['job_id'], lambda j: {'execution': {**j['execution'], 'clock_domain': 'foreign-domain'}})
        with self.assertRaises(DataError) as caught: self.op.check()
        self.assertEqual(caught.exception.code, 'operation_authority_unknown')

    def test_file_replacement_and_expired_deadline_are_not_cached(self):
        original = self.hub.path.read_bytes(); other = self.root/'replacement.bin'
        other.write_bytes(original); os.replace(other, self.hub.path)
        self.op.check()
        self.op.deadline_ns = time.monotonic_ns()-1
        with self.assertRaises(DataError): self.op.check()

    def test_writable_snapshot_rejects_new_tail_even_after_read_cache(self):
        self.hub.assert_writable()
        with self.hub.path.open('ab') as stream: stream.write(b'\x00\x00')
        self.hub.state()  # GET may expose only the last complete committed prefix.
        with self.assertRaises(DataError) as caught: self.hub.assert_writable()
        self.assertEqual(caught.exception.code, 'control_tail_unconfirmed')

    def test_valid_foreign_hub_replacement_cannot_keep_writable_identity(self):
        self.hub.assert_writable()
        foreign=ControlHub(Path(mkdtemp(prefix='retrolume-foreign-hub-',dir=os.environ.get('S08_EVIDENCE'))))
        try:
            self.hub.path.write_bytes(foreign.path.read_bytes())
            with self.assertRaises(DataError):self.hub.assert_writable()
        finally:foreign.lock.close();foreign.operation_lock.close()

    def test_writable_snapshot_observes_peer_fence_and_current_tamper(self):
        self.hub.assert_writable()
        peer = ControlHub(self.root)
        try:
            peer.commit('maintenance.fence', {'state':'frozen'})
            self.assertEqual(self.hub.assert_writable()['fence'], {'state':'frozen'})
            path=self.hub.path; info=path.stat(); raw=bytearray(path.read_bytes())
            raw[40] ^= 1; path.write_bytes(raw); os.utime(path, ns=(info.st_atime_ns,info.st_mtime_ns))
            with self.assertRaises(DataError): self.hub.assert_writable()
        finally: peer.lock.close(); peer.operation_lock.close()

    def foreign_write_refused(self, action):
        """D01：有效B日志取代已读缓存的A，三个写入口均不得追加或返回B事实。"""
        self.hub.state()
        foreign=ControlHub(Path(mkdtemp(prefix='s08-foreign-write-',dir=os.environ.get('S08_EVIDENCE'))))
        try:
            command=DataJobCommand('restore',self.job['business_key'],{'plan_id':str(uuid4()),'plan_sha256':'0'*64})
            context=DataContext(foreign.control_id,0,str(uuid4()),str(uuid4()),'normal')
            job=foreign.create_or_get_job(command,context)
            raw=foreign.path.read_bytes();self.hub.path.write_bytes(raw)
            invoked=[]
            def decide(value):invoked.append(value);return {'stage':'错误混入B'}
            with self.assertRaises(DataError) as caught:
                if action=='commit':self.hub.commit('maintenance.fence',{'state':'frozen'})
                elif action=='same-key':self.hub.create_or_get_job(command,context)
                else:self.hub.change_job(job['job_id'],decide)
            self.assertEqual(caught.exception.code,'control_corrupt')
            self.assertEqual(self.hub.path.read_bytes(),raw)
            self.assertEqual(invoked,[])
        finally:foreign.lock.close();foreign.operation_lock.close()

    def test_foreign_log_commit_rejects_without_append(self):self.foreign_write_refused('commit')
    def test_foreign_log_same_business_key_cannot_return_foreign_job(self):self.foreign_write_refused('same-key')
    def test_foreign_log_change_known_foreign_job_never_calls_decide(self):self.foreign_write_refused('change')

    def test_all_write_entries_refuse_readable_committed_prefix_with_tail(self):
        with self.hub.path.open('ab') as stream:stream.write(b'\x00\x00')
        self.hub.state();raw=self.hub.path.read_bytes()
        command=DataJobCommand('restore',self.job['business_key'],{'plan_id':str(uuid4()),'plan_sha256':'0'*64})
        origin=DataContext(self.hub.control_id,0,str(uuid4()),str(uuid4()),'normal')
        for call in (lambda:self.hub.commit('maintenance.fence',{}),lambda:self.hub.create_or_get_job(command,origin),lambda:self.hub.change_job(self.job['job_id'],lambda _:{})):
            with self.assertRaises(DataError) as caught:call()
            self.assertEqual(caught.exception.code,'control_tail_unconfirmed')
            self.assertEqual(self.hub.path.read_bytes(),raw)


if __name__ == '__main__': unittest.main()
