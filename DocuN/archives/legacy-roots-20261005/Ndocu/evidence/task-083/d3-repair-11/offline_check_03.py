"""Final repair11 offline gate and finite pre/post evidence; never opens a real resource."""
import ast
import difflib
import hashlib
from pathlib import Path
import sys
import unittest
ROOT=Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVID=ROOT/"Ndocu/evidence/task-083/d3-repair-11"
if sys.flags.optimize!=0: raise RuntimeError("offline assertions require optimize=0")
paths=(
 "backend/app/activities/repository.py","backend/app/worker/session.py",
 "backend/tests/test_d3_recovery.py","backend/tests/fixtures/task083/d3_pg_windows.py",
 "backend/tests/test_d3_runner_control.py","Ndocu/evidence/task-083/d3-repair-11/controlled_child.py",
 "Ndocu/evidence/task-083/d3-repair-11/contracts.py",
 "Ndocu/evidence/task-083/d3-repair-11/runner.py",
)
for rel in paths:
    raw=(ROOT/rel).read_bytes(); compile(raw,str(ROOT/rel),"exec")
    print(f"COMPILE_OK {rel} {hashlib.sha256(raw).hexdigest()}",flush=True)
fixture=ast.parse((ROOT/"backend/tests/fixtures/task083/d3_pg_windows.py").read_text(encoding="utf-8"))
ledger=next(n for n in fixture.body if isinstance(n,ast.FunctionDef) and n.name=="ledger_cases")
assigns={target.id:value for n in ast.walk(ledger) if isinstance(n,ast.Assign)
         for target in n.targets if isinstance(target,ast.Name) for value in (n.value,)}
def keyword(call,name):
    return next((k.value for k in call.keywords if k.arg==name),None)
second=assigns["second"].args[0]
upper=assigns["upper"].args[0]
if not (isinstance(keyword(second,"running_owner_session_id"),ast.Constant)
        and keyword(second,"running_owner_session_id").value==0
        and keyword(second,"expected_previous_generation") is not None
        and isinstance(keyword(upper,"running_owner_session_id"),ast.Constant)
        and keyword(upper,"running_owner_session_id").value==4294967295
        and keyword(upper,"expected_previous_generation") is None):
    raise AssertionError("F1 same-SID recovery / separate pending upper-bound call drift")
migration=next(n for n in fixture.body if isinstance(n,ast.FunctionDef) and n.name=="migration_cases")
if "psycopg.errors.CheckViolation" not in [ast.unparse(n.type) for n in ast.walk(migration) if isinstance(n,ast.ExceptHandler)]:
    raise AssertionError("F2 exception class drift")
barrier=next(n for n in fixture.body if isinstance(n,ast.FunctionDef) and n.name=="lock_barrier_case")
if sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="observe_source_lock_wait" for n in ast.walk(barrier))!=2:
    raise AssertionError("source-lock wait observation missing")
print("STATIC_F1_F2_BARRIER_OK (preparation only; no PG transaction proof)",flush=True)
sys.path[:0]=[str(ROOT/"backend/tests"),str(ROOT/"backend"),str(EVID)]
ids=("test_d3_runner_control.ControllerTests.test_runner_import_does_not_touch_resources",
     "test_d3_runner_control.ControllerTests.test_optimization_guard")
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
if not result.wasSuccessful(): sys.exit(1)
pre=EVID/"pre"
oldrunner="Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py"
pairs=[(pre/(rel.replace("/","__")),ROOT/rel,rel) for rel in paths[:4]]
pairs += [(None,ROOT/rel,rel) for rel in paths[4:]]
with (EVID/"incremental.diff").open("w",encoding="utf-8",newline="\n") as out:
    for before,current,label in pairs:
        a=before.read_text(encoding="utf-8").splitlines(keepends=True) if before else []
        b=current.read_text(encoding="utf-8").splitlines(keepends=True)
        out.writelines(difflib.unified_diff(a,b,fromfile="pre/"+label if before else "/dev/null",tofile=label))
old=(pre/(oldrunner.replace("/","__"))).read_text(encoding="utf-8").splitlines(keepends=True)
new=(EVID/"runner.py").read_text(encoding="utf-8").splitlines(keepends=True)
(EVID/"runner-old-to-new.diff").write_text("".join(difflib.unified_diff(old,new,fromfile=oldrunner,tofile="Ndocu/evidence/task-083/d3-repair-11/runner.py")),encoding="utf-8")
unchanged={
 "backend/migrations/006_activities_running_owner_session.sql":"F791F22DCFCCF204F6FDA369470978452B3B23CCA0FC40D2057BD08EA47F6428",
 "backend/app/worker/windows_job.py":"D04ED8F249106328D81147707451E6092C2D650C9199BD6C4989931D5249C596",
 "backend/tests/test_worker_session.py":"4027F5CD72B17D826626704E118B0A194B0A7AEF48C4EE4C8DE4AC3EFAE69CF5",
 "backend/tests/fixtures/task083/offline_unit.py":"BB30163891DE46EF97350B90C1988DF5C5E0F80189DD13CDCCB9E9C3C8264B6D",
 oldrunner:"39E5917E0173ACED0391F9729A4A3CE2F492ED41B8BB2C41E7CD205CC735A27F",
}
lines=[]
for rel in (*paths,*unchanged):
    digest=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest().upper()
    if rel in unchanged and digest!=unchanged[rel]: raise AssertionError("unchanged frozen file drift: "+rel)
    lines.append(f"{rel} {digest} {'UNCHANGED_REVIEW07' if rel in unchanged else 'REPAIR11'}")
(EVID/"final-hashes.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"OFFLINE_RESULT ran={result.testsRun} failures=0 errors=0 diff=incremental.diff hashes=final-hashes.txt",flush=True)