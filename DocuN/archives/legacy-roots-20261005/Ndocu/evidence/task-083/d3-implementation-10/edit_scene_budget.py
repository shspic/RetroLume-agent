from pathlib import Path
p=Path("backend/tests/fixtures/task083/d3_pg_windows.py")
s=p.read_text(encoding="utf-8")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:100]))
 s=s.replace(a,b,1)
rep('def windows_case():\n    name, scoped=make_schema("windows")', 'def windows_case():\n    scene_started=time.monotonic()\n    name, scoped=make_schema("windows")')
rep('    assert elapsed<=30,elapsed\n    emit({"phase":"windows_recovery"', '    scene_elapsed=time.monotonic()-scene_started\n    assert scene_elapsed<=30,scene_elapsed\n    emit({"phase":"windows_recovery"')
rep('"transaction_committed":True,"mutex_release":"SUP outcome returned after DB settlement"})', '"transaction_committed":True,"scene_seconds":scene_elapsed,\n          "mutex_release":"SUP outcome returned after DB settlement"})')
p.write_text(s,encoding="utf-8")
