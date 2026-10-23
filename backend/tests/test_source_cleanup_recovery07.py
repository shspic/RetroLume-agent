"""Local journal negatives for cleanup authority; actual PG retry has root evidence."""
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from app.data_exit.contracts import DataContext,DataJobCommand,DataError,canonical
from app.data_exit.control import ControlHub
from app.data_exit.deletions import _CleanupAttempt
from app.data_exit.operations import Operation
from tests.fixtures.task120.offline import store


class CleanupRecoveryTests(TestCase):
    def test_new_cleanup_attempt_cannot_restore_old_execution_or_admit(self):
        hub=store().hub;source=hub.state()['source']
        scope={'source_id':str(uuid4()),'expected_revision':1,'impact_sha256':'a'*64}
        job=hub.create_or_get_job(DataJobCommand('source_delete',str(uuid4()),scope),
            DataContext(hub.control_id,0,source['dataset_id'],source['instance_id'],'normal'))
        old=Operation(hub,job['job_id'],10,'checking_deletion');old.admit('source_tombstone_commit')
        old.finish('deleted_pending')
        original=deepcopy(hub.execution_job(job['job_id'])['execution'])
        tomb={'tombstone_id':str(uuid4()),'entity_kind':'source','entity_id':scope['source_id'],
            'business_id_observed':job['business_key'],'manifest_sha256':scope['impact_sha256'],'effective_revision':2}
        with patch('app.data_exit.operations.CLOCK_DOMAIN','new-process'):
            with self.assertRaises(DataError):Operation.resume_cleanup(hub,job['job_id'])
            fresh=_CleanupAttempt(hub,job['job_id'],10)
            with self.assertRaises(DataError):fresh.admit('source_tombstone_commit')
            with self.assertRaises(DataError):fresh.finish('deleted')
            with self.assertRaises(DataError):fresh.confirm_tombstone({**tomb,'manifest_sha256':'b'*64})
            fresh.confirm_tombstone(tomb)
            with patch('app.data_exit.operations.CLOCK_DOMAIN','other-process'):
                with self.assertRaises(DataError):fresh.check()
            # A replacement attempt invalidates the old actor/revision, even
            # when both have the same boot/process domain.
            replacement=_CleanupAttempt(hub,job['job_id'],10)
            with self.assertRaises(DataError):fresh.check()
            replacement.confirm_tombstone(tomb)
            with patch('app.data_exit.deletions.time.monotonic_ns',return_value=replacement.deadline_ns):
                with self.assertRaises(DataError):replacement.check()
            receipt=replacement.finish('deleted')
            self.assertEqual(receipt['state'],'deleted')
            with self.assertRaises(DataError):replacement.finish('deleted')
            with self.assertRaises(DataError):_CleanupAttempt(hub,job['job_id'],10)
        self.assertEqual(canonical(hub.execution_job(job['job_id'])['execution']),canonical(original))
        reopened=ControlHub(hub.root)
        self.assertEqual(reopened.get(job['job_id'])['state'],'deleted')
        events=hub._read()[0]
        admissions=[e for e in events if e['kind']=='job.update' and
            e['payload'].get('execution',{}).get('admission')]
        self.assertEqual(len(admissions),1)
