"""本卡定向离线检查；禁止真实 Docker/PG/Windows 子进程。"""
import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'backend/tests'),str(ROOT/'Ndocu/evidence/task-083/d3-repair-11')]
import runner
from contracts import SCENARIOS, expected_scenarios, validate_records
from test_d3_runner_control import ControllerTests


def projection():
    return [runner.CID,runner.NAME,runner.IMAGE,json.dumps({'retrolume-task':'083','phase':'d3-10','run':'20260925-195448'}),
            'false',json.dumps([{'Type':'volume','Name':runner.VOLUME,'Destination':'/var/lib/postgresql/data'}]),
            '1000000000','536870912','128','no','bridge',json.dumps({'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'55439'}]}),'null','null']


class CompletionChecks(unittest.TestCase):
    def test_projection_fails_closed(self):
        original=projection()
        for configured in ('null','[]'):
            fields=original.copy(); fields[-1]=configured
            self.assertTrue(runner.valid_identity(runner.parse_inspect('|'.join(fields))))
        fields=original.copy(); fields[-1]='[{"Type":"bind","Source":"unexpected"}]'
        self.assertFalse(runner.valid_identity(runner.parse_inspect('|'.join(fields))))
        for index,value in ((4,'unknown'),(4,'False'),(13,'{}'),(13,'false'),(13,'0'),(13,'"null"'),(13,'{'),(5,'null'),(3,'[]'),(11,'[]')):
            fields=original.copy(); fields[index]=value
            with self.subTest(index=index,value=value),self.assertRaises((ValueError,RuntimeError)):
                runner.parse_inspect('|'.join(fields))
        with self.assertRaises(RuntimeError): runner.parse_inspect('|'.join(original[:-1]))
        value=runner.parse_inspect('|'.join(original)); value['port_bindings']['123/tcp']=[]
        self.assertFalse(runner.valid_identity(value))
        with patch.object(runner,'docker',return_value=SimpleNamespace(returncode=0,stdout='|'.join(original))) as call:
            runner.inspect((time.monotonic()+300,))
        template=call.call_args.args[0][2]
        self.assertEqual(len(template.split('|')),14)
        self.assertIn('{{json (index .HostConfig "Mounts")}}',template)
        self.assertNotIn('Config.Env',template)

    def test_readiness_then_role_auth_and_single_rotation(self):
        replies=[SimpleNamespace(returncode=n,stdout='') for n in (2,1,0)]
        replies += [SimpleNamespace(returncode=0,stdout=runner.USER+'|'+runner.DB+'\n'),SimpleNamespace(returncode=0,stdout='')]
        connection=unittest.mock.MagicMock()
        connection.__enter__.return_value.execute.return_value.fetchone.return_value=(runner.USER,runner.DB,5432)
        with patch.object(runner,'docker',side_effect=replies) as call,patch.object(runner.psycopg,'connect',return_value=connection),patch.object(runner.time,'sleep'),patch.object(runner.secrets,'token_hex',return_value='synthetic-secret'):
            dsn,password,identity=runner.local_auth_and_rotate((time.monotonic()+300,))
        self.assertEqual(identity['rotation_count'],1)
        self.assertEqual(call.call_count,5)
        self.assertNotIn(password,repr(call.call_args.args))
        self.assertIn('ALTER ROLE',call.call_args.kwargs['input_text'])
        runner.REDACTIONS.clear()
        replies=[SimpleNamespace(returncode=0,stdout=''),SimpleNamespace(returncode=2,stdout='')]
        with patch.object(runner,'docker',side_effect=replies) as call,self.assertRaisesRegex(RuntimeError,'auth'):
            runner.local_auth_and_rotate((time.monotonic()+300,))
        self.assertEqual(call.call_count,2)

    def test_partial_reuse_and_dependency_hash(self):
        parts=tuple(SCENARIOS)
        lines=[]
        for scene in SCENARIOS['migration']:
            lines += [json.dumps({'phase':'scenario_start','scenario':scene}),json.dumps({'phase':scene})]
        lines.append(json.dumps({'phase':'scenario_start','scenario':SCENARIOS['ledger'][0]}))
        contract=validate_records('\n'.join(lines),parts,1,cleanup_confirmed=True)
        meta={'parts':list(parts),'contract':contract,'outer_tree_zero':True,'cleanup_error':None,'windows_started':False,'timeout':False,'error':None,'exit_code':1}
        self.assertEqual(runner.reusable_parts(meta),('migration',))
        self.assertFalse(contract['pass'])
        for change in ({'windows_started':True},{'outer_tree_zero':False},{'timeout':True},{'error':'control failure'}):
            self.assertEqual(runner.reusable_parts(dict(meta,**change)),())
        original=runner.FIXTURE.read_bytes()
        changed=original.replace(b'def ledger_cases():',b'def ledger_cases():\n    repair_probe = 1')
        first,second=runner.source_fingerprints(original),runner.source_fingerprints(changed)
        self.assertEqual(first['migration'],second['migration'])
        self.assertNotEqual(first['ledger'],second['ledger'])
        self.assertEqual(len(expected_scenarios(parts)),8)


if __name__=='__main__':
    for path in [Path(runner.__file__),Path(runner.__file__).with_name('controlled_child.py'),Path(runner.__file__).with_name('contracts.py'),runner.FIXTURE]:
        compile(path.read_bytes(),str(path),'exec')
    # 原有控制替身只定向复核其直接使用方；不运行旧 Job/PG 实验。
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(CompletionChecks),unittest.defaultTestLoader.loadTestsFromTestCase(ControllerTests)])
    with patch('subprocess.run',side_effect=AssertionError('unmocked resource execution')),patch('psycopg.connect',side_effect=AssertionError('unmocked database connection')):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
