"""采用明确续作额度，原账/结果先封存；首次接卡计时不重开原截止。"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import time
from .control import ROOT,EVIDENCE,atomic

C01=EVIDENCE/"continuation-01"
PERMIT="TASK-111-G11-C01-20261010"


def main():
    C01.mkdir(exist_ok=False);pre=C01/"pre";pre.mkdir()
    card=ROOT/"DocuN/tasks/TASK-111.md";authority=ROOT/"DocuN/evidence/TASK-111/orchestration-receipt-01/continuation-budget.json"
    issued=json.loads(authority.read_text(encoding="utf-8-sig"));budget=json.loads((EVIDENCE/"budget.json").read_text(encoding="utf-8"))
    result=ROOT/"DocuN/results/TASK-111-result.md";raw=result.read_bytes()
    if len(raw)!=25338 or hashlib.sha256(raw).hexdigest()!="72bb21f612fcee8287c77099383721986ed844fc8e290eacf23e9f501afd2fe0":raise RuntimeError("returned result changed")
    if issued["permit"]!=PERMIT or budget["active_batch"] is not None or budget["counts"]!=issued["consumed_at_issue"] or budget["deadline_ns"]!=902913370092600:raise RuntimeError("continuation binding")
    for path in (EVIDENCE/"budget.json",EVIDENCE/"events.jsonl",result,card,authority):shutil.copy2(path,pre/path.name)
    now=time.monotonic_ns();utc=datetime.now(timezone.utc)
    first=datetime(2026,10,10,6,5,13,tzinfo=timezone.utc);start=now-int((utc-first).total_seconds()*1e9)
    value={"permit":PERMIT,"base_permit":budget["permit"],"started_ns":start,"original_deadline_ns":budget["deadline_ns"],
       "phase":"implementation_offline","phase_start_ns":now,"used_seconds":{"metadata":(now-start)/1e9,"implementation_offline":0.0,"real":0.0},
       "caps_seconds":{"metadata":1200,"implementation_offline":3600,"real":10500},"first_known_utc":"2026-10-10T06:05:18Z","conservative_margin":5,
       "old_category_unknown":True,"metadata_read_complete_ns":now,"caps_after":issued["caps_after"],"execution_started":True}
    if value["used_seconds"]["metadata"]>1200 or now>=budget["deadline_ns"]:raise RuntimeError("continuation preparation window exceeded")
    budget["continuation_permit"]=PERMIT;budget["continuation_caps"]=issued["caps_after"]
    atomic(C01/"timing.json",value);atomic(EVIDENCE/"budget.json",budget)
    affected=["backend/app/preview/process.py","backend/app/preview/host_policy.py","backend/app/preview/docker_control.py","backend/app/preview/production_supervisor.py","backend/app/preview/production_reaper.py",
      "backend/tests/fixtures/task111/control.py","backend/tests/fixtures/task111/core.py","backend/tests/fixtures/task111/server.py","backend/tests/fixtures/task111/http_matrix.py",
      "frontend/tests/task111/browser.cjs","deploy/preview/collect_licenses.py","deploy/preview/renderer-host.cjs","frontend/src/explanations/HtmlExplanationPanel.tsx","frontend/src/explanations/htmlApi.ts"]
    rows=[]
    for relative in affected:
        path=ROOT/relative;destination=pre/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination)
        rows.append({"path":relative,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    atomic(C01/"pre-source.json",rows)
    print(json.dumps({"accepted":PERMIT,"deadline_ns":budget["deadline_ns"],"metadata_seconds":value["used_seconds"]["metadata"]}))


if __name__=="__main__":main()
