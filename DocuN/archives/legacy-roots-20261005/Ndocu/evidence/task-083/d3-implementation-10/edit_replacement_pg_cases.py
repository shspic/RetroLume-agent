from pathlib import Path
p=Path("backend/tests/fixtures/task083/d3_pg_windows.py")
s=p.read_text(encoding="utf-8")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:100]))
 s=s.replace(a,b,1)
rep('    assert run_async(ledger.inspect_window(activity)).running_owner_session_id==0\n    expire(scoped,activity)\n', '''    snapshot=run_async(ledger.inspect_window(activity))
    assert snapshot.running_owner_session_id==0 and not snapshot.lease_recoverable
    try:
        run_async(ledger.claim_lease(activity,"too_early",lease_seconds=6,window_seconds=6,
                                     running_owner_session_id=0,expected_previous_generation=first.execution_generation))
    except ActivityLedgerConflict: pass
    else: raise AssertionError("active database lease was stolen")
    assert row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id FROM activities WHERE id=%s",(activity,))==before
    emit({"phase":"ledger_active_lease_rejected","schema":name,"activity":activity,"row":before})
    expire(scoped,activity)
    try:
        run_async(ledger.claim_lease(activity,"wrong_owner",lease_seconds=6,window_seconds=6,
                                     running_owner_session_id=8,expected_previous_generation=first.execution_generation))
    except ActivityLedgerConflict: pass
    else: raise AssertionError("mismatched old session was accepted")
''')
rep('        lambda: run_async(ledger.begin_window_close(activity,"old",first.execution_generation)),\n', '''        lambda: run_async(ledger.begin_window_close(activity,"old",first.execution_generation)),
        lambda: run_async(ledger.settle_execution_window(activity,"old",first.execution_generation,
                                                       window_seconds=6,elapsed_seconds=1)),
''')
p.write_text(s,encoding="utf-8")
