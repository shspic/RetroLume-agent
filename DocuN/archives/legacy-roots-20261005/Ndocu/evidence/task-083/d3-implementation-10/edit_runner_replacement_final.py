from pathlib import Path
p=Path("Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py")
s=p.read_text(encoding="utf-8")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:100]))
 s=s.replace(a,b,1)
rep("DEADLINE=T0+1800","DEADLINE=T0+1680  # replacement remaining resource+real-run budget: 28 minutes")
rep('    phases=[]\n    for line in text_out.splitlines():\n        try: phases.append(json.loads(line).get("phase"))\n        except json.JSONDecodeError: pass\n    meta={"parts":parts,"pid":proc.pid,"created_100ns":created,"exit":proc.returncode,\n          "elapsed_seconds":time.monotonic()-started,"timeout_killed":killed,"phases":phases}',
'''    records=[]
    for line in text_out.splitlines():
        try:
            parsed=json.loads(line)
            if isinstance(parsed,dict): records.append(parsed)
        except json.JSONDecodeError: pass
    phases=[record.get("phase") for record in records]
    windows_started=any(record.get("label")=="windows" and record.get("phase")=="schema" for record in records)
    meta={"parts":parts,"pid":proc.pid,"created_100ns":created,"exit":proc.returncode,
          "elapsed_seconds":time.monotonic()-started,"timeout_killed":killed,
          "phases":phases,"windows_started":windows_started}''')
rep('    log(f"batch {number} exit={proc.returncode} elapsed={meta[\'elapsed_seconds\']:.2f}s phases={phases} pass={ok}")\n    return ok',
'''    log(f"batch {number} exit={proc.returncode} elapsed={meta['elapsed_seconds']:.2f}s phases={phases} pass={ok}")
    # A failed Windows phase has no positive whole-tree cleanup proof; stop, never retry.
    return ok, (not killed and not windows_started)''')
rep('        if batch(parts,number,dsn):\n            state["verdict"]="PASS";break\n        state["verdict"]=f"ATTEMPT_{number}_FAILED";save()',
'''        passed,safe_retry=batch(parts,number,dsn)
        if passed:
            state["verdict"]="PASS";break
        if not safe_retry:
            state["verdict"]=f"ATTEMPT_{number}_FAILED_STOP"
            save()
            break
        state["verdict"]=f"ATTEMPT_{number}_FAILED";save()''')
p.write_text(s,encoding="utf-8")
