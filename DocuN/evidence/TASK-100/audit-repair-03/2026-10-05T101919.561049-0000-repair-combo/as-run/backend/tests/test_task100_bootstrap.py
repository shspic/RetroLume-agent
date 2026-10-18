"""Offline execution of the actual bootstrap guard; no PG or real fixture install."""
import os
import runpy
import socket
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch

class RepairBootstrapTests(unittest.TestCase):
    def test_actual_current_permit_installs_and_ended_or_mismatched_permit_fails_closed(self):
        current='TASK-100-audit-repair-03-20261005';old='TASK-100-continuation-02-20261004'
        script=Path(__file__).parent/'fixtures/task100/bootstrap/sitecustomize.py'
        for fixture,permit,allowed in ((current,current,True),(old,current,False),(current,old,False)):
            install=Mock();exit_mock=Mock(side_effect=SystemExit(86))
            with (patch.dict(os.environ,{'RETROLUME_TASK100_FIXTURE':fixture,'RETROLUME_TASK100_PERMIT':permit}),
                  patch.dict('sys.modules',{'tests.fixtures.task100.fixture_runtime':SimpleNamespace(install=install)}),
                  patch.object(socket.socket,'connect',socket.socket.connect),
                  patch.object(socket.socket,'connect_ex',socket.socket.connect_ex),patch.object(os,'_exit',exit_mock)):
                if allowed:runpy.run_path(str(script));install.assert_called_once();exit_mock.assert_not_called()
                else:
                    with self.assertRaises(SystemExit) as rejection:runpy.run_path(str(script))
                    self.assertEqual(rejection.exception.code,86);install.assert_not_called()
