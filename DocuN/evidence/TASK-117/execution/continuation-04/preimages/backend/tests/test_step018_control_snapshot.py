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
        self.root = Path(mkdtemp(prefix='retrolume-snapshot-check-'))
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


if __name__ == '__main__': unittest.main()
