"""只接收明确C02增量，先封存原件并固化首次读取截止。"""
from datetime import datetime,timezone
import hashlib,json,os,shutil,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"DocuN/evidence/TASK-111/execution"
C02=EVIDENCE/"continuation-02"


def main():
    authority=ROOT/"DocuN/evidence/TASK-111/orchestration-receipt-02/continuation-budget.json"
    issued=json.loads(authority.read_text(encoding="utf-8-sig"));budget=json.loads((EVIDENCE/"budget.json").read_text())
    result=ROOT/"DocuN/results/TASK-111-result.md";raw=result.read_bytes()
    if issued["permit"]!="TASK-111-G11-C02-20261010" or budget["counts"]!=issued["used_counts"] or budget["active_batch"] is not None:raise RuntimeError("C02 binding")
    if len(raw)!=42608 or hashlib.sha256(raw).hexdigest()!=issued["source_result"]["sha256"]:raise RuntimeError("C02 prior result")
    C02.mkdir(exist_ok=False);pre=C02/"pre";pre.mkdir()
    for path in (EVIDENCE/"budget.json",EVIDENCE/"events.jsonl",result,ROOT/"DocuN/tasks/TASK-111.md",authority):shutil.copy2(path,pre/path.name)
    now=time.monotonic_ns();utc=datetime.now(timezone.utc);first=datetime(2026,10,10,8,48,58,tzinfo=timezone.utc)
    start=now-int((utc-first).total_seconds()*1e9);deadline=min(start+21600*10**9,issued["seconds"]["aggregate_deadline_ns_after"])
    value={"permit":issued["permit"],"base_permit":issued["base_permit"],"first_read_utc":first.isoformat(),"start_ns":start,
      "deadline_ns":deadline,"business_deadline_ns":deadline-600*10**9,"phase":"metadata","phase_start_ns":start,
      "used_seconds":{"metadata":0.0,"implementation_offline":0.0,"real":0.0,"cleanup":0.0},"hard_count_caps":issued["hard_count_caps"],
      "classification_only":True,"old_unknown_preserved":True,"C01_breach_preserved":True,"original_deadline_ns":budget["deadline_ns"]}
    def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    save(C02/"timing.json",value)
    budget["original_deadline_ns"]=budget["deadline_ns"];budget["deadline_ns"]=deadline;budget["business_deadline_ns"]=value["business_deadline_ns"]
    budget["continuation_permit"]=issued["permit"];budget["continuation_caps"]=issued["hard_count_caps"];save(EVIDENCE/"budget.json",budget)
    targets=list((ROOT/"backend/app/preview").glob("*.py"))+list((ROOT/"backend/tests/fixtures/task111").glob("*.py"))+[
       ROOT/"frontend/tests/task111/browser.cjs",ROOT/"deploy/preview/renderer-host.cjs",ROOT/"deploy/preview/collect_licenses.py"]
    rows=[]
    for path in targets:
        relative=path.relative_to(ROOT);destination=pre/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination)
        rows.append({"path":relative.as_posix(),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    save(C02/"pre-source.json",rows)
    print(json.dumps({"accepted":issued["permit"],"deadline_utc":datetime.fromtimestamp(utc.timestamp()+(deadline-now)/1e9,timezone.utc).isoformat(),"counts_preserved":budget["counts"]}))


if __name__=="__main__":main()
