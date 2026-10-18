"""Pure D3 controller substitutes: no Job, process, Docker, or PG."""
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"Ndocu/evidence/task-083/d3-repair-11")]
from contracts import deadline_left,expected_scenarios,parse_parts,validate_records
from controlled_child import ControlledChild,OwnershipUnknown
from app.worker.windows_job import _BASIC_ACCOUNTING,_PROCESS_INFORMATION,_FILETIME

class Kernel:
    def __init__(self,fail=None): self.fail=fail; self.events=[]; self.active=0; self.query_fail=False; self.close_fail=False
    def CreateJobObjectW(self,*a): self.events.append("job"); return 100
    def SetInformationJobObject(self,*a): return 1
    def CreateProcessW(self,*a):
        self.events.append("create")
        if self.fail=="create": return 0
        p=ctypes.cast(a[-1],ctypes.POINTER(_PROCESS_INFORMATION)).contents
        p.hProcess=201; p.hThread=202; p.dwProcessId=203
        return 1
    def GetProcessTimes(self,h,created,*a):
        self.events.append("identity")
        if self.fail=="identity": return 0
        ctypes.cast(created,ctypes.POINTER(_FILETIME)).contents.dwLowDateTime=1234
        return 1
    def AssignProcessToJobObject(self,*a):
        self.events.append("assign")
        if self.fail=="assign": return 0
        self.active=1; return 1
    def QueryInformationJobObject(self,h,k,data,*a):
        if self.query_fail: return 0
        ctypes.cast(data,ctypes.POINTER(_BASIC_ACCOUNTING)).contents.ActiveProcesses=self.active
        return 1
    def ResumeThread(self,*a): self.events.append("resume"); return 1
    def TerminateProcess(self,*a): self.events.append("terminate_exact"); return 1
    def TerminateJobObject(self,*a): self.events.append("terminate_outer"); self.active=0; return 1
    def WaitForSingleObject(self,*a): return 0
    def GetExitCodeProcess(self,h,p): ctypes.cast(p,ctypes.POINTER(ctypes.c_ulong)).contents.value=0; return 1
    def CloseHandle(self,*a): return 0 if self.close_fail else 1

class ControllerTests(unittest.TestCase):
    def test_pre_resume_failures(self):
        for failure in ("create","identity","assign"):
            with self.subTest(failure=failure):
                api=Kernel(failure); child=ControlledChild(api)
                with self.assertRaises(OwnershipUnknown):
                    child.start([sys.executable],cwd=ROOT,env={"X":"1"},deadline=time.monotonic()+5)
                self.assertNotIn("resume",api.events)
                if failure!="create": self.assertIn("terminate_exact",api.events)
                self.assertTrue(child.cleanup_confirmed)
    def test_deadline_and_query_unknown(self):
        api=Kernel(); child=ControlledChild(api)
        with self.assertRaises(TimeoutError):
            child.start([sys.executable],cwd=ROOT,env={},deadline=time.monotonic()-1)
        self.assertEqual(api.events,[])
        identity=child.start([sys.executable],cwd=ROOT,env={},deadline=time.monotonic()+5)
        self.assertEqual(identity,{"pid":203,"created_100ns":1234})
        self.assertLess(api.events.index("identity"),api.events.index("assign"))
        self.assertLess(api.events.index("assign"),api.events.index("resume"))
        api.query_fail=True
        with self.assertRaises(OwnershipUnknown): child.stop(time.monotonic()+5)
        self.assertFalse(child.cleanup_confirmed)
        child.close()
    def test_close_failure_marks_cleanup_unknown(self):
        api=Kernel(); child=ControlledChild(api)
        child.start([sys.executable],cwd=ROOT,env={},deadline=time.monotonic()+5)
        child.stop(time.monotonic()+5)
        self.assertTrue(child.cleanup_confirmed)
        api.close_fail=True
        with self.assertRaises(OwnershipUnknown): child.close()
        self.assertFalse(child.cleanup_confirmed)
    def test_exact_results_and_deadlines(self):
        parts=parse_parts("migration,ledger")
        lines=[]
        for name in expected_scenarios(parts):
            lines += [json.dumps({"phase":"scenario_start","scenario":name}),json.dumps({"phase":name})]
        lines.append(json.dumps({"phase":"complete","all_pass":True,"parts":list(parts)}))
        raw="\n".join(lines)+"\n"
        self.assertTrue(validate_records(raw,parts,0,cleanup_confirmed=True)["pass"])
        for bad in (raw.replace('"all_pass": true','"all_pass": false'),raw+lines[1]+"\n",
                    raw.replace('"phase": "complete"','"phase": "unknown"'),"\n".join(lines[:2]+lines[-1:])):
            self.assertFalse(validate_records(bad,parts,0,cleanup_confirmed=True)["pass"])
        for exit_code,clean in ((1,True),(0,False)):
            self.assertFalse(validate_records(raw,parts,exit_code,cleanup_confirmed=clean)["pass"])
        self.assertFalse(validate_records(raw,parts,0,cleanup_confirmed=True,timed_out=True)["pass"])
        with self.assertRaises(ValueError): parse_parts("migration,migration")
        with self.assertRaises(TimeoutError): deadline_left(time.monotonic()+.2,reserve=1)
    def test_runner_import_does_not_touch_resources(self):
        with patch("subprocess.run",side_effect=AssertionError("resource command on import")), patch(
            "psycopg.connect",side_effect=AssertionError("PG connect on import")
        ):
            import runner
        self.assertEqual(runner.CID,"85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7")
    def test_unknown_cleanup_and_windows_start_block_retry(self):
        import runner
        base={"contract":{"pass":False},"outer_tree_zero":True,"cleanup_error":None,"windows_started":False}
        self.assertTrue(runner.retry_allowed(base))
        for changed in ({"outer_tree_zero":False},{"cleanup_error":"query unknown"},{"windows_started":True}):
            case=dict(base,**changed)
            self.assertFalse(runner.retry_allowed(case))
    def test_optimization_guard(self):
        path=ROOT/"backend/tests/fixtures/task083/d3_pg_windows.py"
        spec=importlib.util.spec_from_file_location("d3_offline_guard",path)
        module=importlib.util.module_from_spec(spec)
        with patch.dict(os.environ,{"RETROLUME_TASK_083_D3_DATABASE_URL":"postgresql://synthetic"}):
            spec.loader.exec_module(module)
        module.require_assertions(0)
        with self.assertRaises(RuntimeError): module.require_assertions(1)

if __name__=="__main__": unittest.main(verbosity=2)