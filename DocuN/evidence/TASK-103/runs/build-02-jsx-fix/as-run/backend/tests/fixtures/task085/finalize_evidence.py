"""只汇总已有证据和文件差异，不启动测试或资源。"""
from pathlib import Path
import difflib
import hashlib
import json
from datetime import datetime,timezone
from run_offline import ROOT,BACKEND,EVID,hashes

def main():
    pre=json.loads((EVID/"pre-hashes.json").read_text(encoding="utf-8-sig"))
    final=hashes()
    (EVID/"post-hashes.json").write_text(json.dumps(final,indent=2),encoding="utf-8")
    changed=[];unexpected=[]
    for item in pre:
        path=ROOT/item["path"]
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        normalized=Path(item["path"]).as_posix()
        if actual.lower()!=item["sha256"].lower():
            changed.append(normalized)
            if not normalized.startswith("backend/app/worker/"):unexpected.append(normalized)
    diffs=[]
    paths=list((BACKEND/"app/worker").glob("*.py"))+[BACKEND/"tests/test_worker_one_call.py"]+list((BACKEND/"tests/fixtures/task085").glob("*.py"))
    for path in sorted(paths):
        relative=path.relative_to(ROOT).as_posix()
        old=EVID/"pre"/relative
        diffs.extend(difflib.unified_diff(old.read_text(encoding="utf-8").splitlines(True) if old.exists() else [],
            path.read_text(encoding="utf-8").splitlines(True),fromfile="pre/"+relative,tofile="post/"+relative))
    (EVID/"task085.diff").write_text("".join(diffs),encoding="utf-8")
    real=EVID/"20260928T001119Z-77ba1b"
    manifest=json.loads((real/"manifest.json").read_text(encoding="utf-8"))
    records=[json.loads(line) for line in (real/"stdout.log").read_text(encoding="utf-8").splitlines() if line.strip()]
    starts=[r["id"] for r in records if r.get("event")=="scenario_start"]
    ends=[r["id"] for r in records if r.get("event")=="scenario_complete"]
    asrun=json.loads((real/"as-run-hashes.json").read_text())
    drift=[p for p,h in asrun.items() if final.get(p)!=h]
    offline=[]
    for p in sorted(EVID.glob("offline-*-meta.json")):
        item=json.loads(p.read_text());offline.append({"file":p.name,"exit":item["exit"],"seconds":item["seconds"]})
    report={"utc":datetime.now(timezone.utc).isoformat(),"changed_existing":changed,"unexpected_pre_drift":unexpected,
            "after_real_drift":drift,"new_since_real":[p for p in final if p not in asrun],
            "real_start_ids":starts,"real_completed_ids":ends,"scenario_count":len(ends),
            "batch_exit":manifest["batch_exit"],"resource_seconds":manifest["seconds"],
            "offline":offline,"offline_total_seconds":sum(r["seconds"] for r in offline),
            "no_provider_network_executed":True,"no_independent_audit_claimed":True,
            "resources_stopped_at_recorded_time":manifest["container_stopped"] and manifest["outer_tree_zero"] and manifest["outer_handles_closed"]}
    (EVID/"delivery-check.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":main()
