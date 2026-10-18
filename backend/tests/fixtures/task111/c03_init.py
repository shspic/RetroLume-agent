"""接收续作03唯一增量，保留旧账和首次读卡计时的不确定边界。"""
from datetime import datetime,timezone
import hashlib,json,os,shutil,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
E=ROOT/"DocuN/evidence/TASK-111/execution"
C03=E/"continuation-03"

def main():
    authority=ROOT/"DocuN/evidence/TASK-111/orchestration-continuation-03/continuation-budget.json"
    issued=json.loads(authority.read_text(encoding="utf-8-sig"));old=json.loads((E/"budget.json").read_text(encoding="utf-8"))
    if (C03/"timing.json").exists():raise RuntimeError("C03 already accepted")
    if issued["permit"]!="TASK-111-G11-C03-20261011" or old["active_batch"] is not None:raise RuntimeError("C03 binding")
    if any(old["counts"][k]!=v for k,v in issued["prior_used"].items()):raise RuntimeError("C03 previous counts drift")
    if any(abs(old["time_seconds"][k]-v)>1e-8 for k,v in issued["prior_time_seconds"].items()):raise RuntimeError("C03 previous time drift")
    pre=C03/"pre-ledger";pre.mkdir(exist_ok=False)
    for p in (E/"budget.json",E/"events.jsonl",authority):shutil.copyfile(p,pre/p.name)
    observation=json.loads((C03/"window-observation.json").read_text(encoding="utf-8"))
    now=time.monotonic_ns();deadline=observation["deadline_monotonic_ns"]
    if now>=deadline-600*10**9:raise RuntimeError("C03 business window exhausted")
    timing={"permit":issued["permit"],"base_permit":old["permit"],"start_ns":observation["conservative_start_monotonic_ns"],
      "deadline_ns":deadline,"deadline_utc":observation["deadline_utc"],"business_deadline_ns":deadline-600*10**9,
      "phase":"metadata","phase_start_ns":observation["conservative_start_monotonic_ns"],
      "used_seconds":{"metadata":0.0,"implementation_offline":0.0,"real":0.0,"cleanup":0.0},
      "hard_count_caps":issued["cumulative_caps"],"new_real_limit_seconds":issued["new_real_limit_seconds"],
      "prior_time_seconds":old["time_seconds"].copy(),"prior_counts":old["counts"].copy(),
      "original_deadline_ns":old["deadline_ns"],"classification_only":True,"old_unknown_preserved":True,
      "first_read_exact_timestamp_available":False,"conservative_margin_seconds":300}
    def save(p,x):
        tmp=p.with_suffix(p.suffix+".new");tmp.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8");os.replace(tmp,p)
    save(C03/"timing.json",timing);save(C03/"preview-name-plan.json",[str(n).zfill(2) for n in range(15,45)])
    old["prior_C02_deadline_ns"]=old["deadline_ns"];old["deadline_ns"]=deadline;old["business_deadline_ns"]=timing["business_deadline_ns"]
    old["continuation_permit"]=issued["permit"];old["continuation_caps"]=issued["cumulative_caps"]
    save(E/"budget.json",old)
    save(C03/"acceptance-receipt.json",{"permit":issued["permit"],"at_utc":datetime.now(timezone.utc).isoformat(),"at_ns":now,
      "old_budget_sha256":hashlib.sha256((pre/"budget.json").read_bytes()).hexdigest(),"old_counts_preserved":True,"old_times_preserved":True,
      "C02_deadline_historical_only":True,"conservative_deadline_utc":observation["deadline_utc"]})
    print(json.dumps({"accepted":issued["permit"],"deadline_utc":observation["deadline_utc"],"counts_preserved":old["counts"]}))

if __name__=="__main__":main()
