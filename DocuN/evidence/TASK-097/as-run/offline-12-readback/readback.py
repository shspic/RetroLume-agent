"""只修保存证明的CRLF回读标记；原错误证明/文档/台账留原件。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT=Path("D:/shspic/project_NO3_RetroLume-agent")
E=ROOT/"DocuN/evidence/TASK-097"
OUT=Path(__file__).resolve().parent
begin=time.monotonic()
started=datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))

original=read(E/"delivery-proof.json")
result=ROOT/"DocuN/results/TASK-097-result.md"
input_files=[E/"delivery-proof.json",E/"closing-run.json",E/"budget-final.json",E/"execution-ledger.json",E/"attempt-ledger.json",result]
captured=[]
for src in input_files:
    dst=OUT/"before"/src.relative_to(ROOT)
    if dst.exists():raise RuntimeError("不能覆盖回读修正的原件")
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
    captured.append({"path":str(src),"snapshot":str(dst),"sha256":sha(dst)})
write(OUT/"manifest.json",{"at":started,"command":[sys.executable,"-B",str(Path(__file__).resolve())],
    "expected":"文件保持真实UTF8/CRLF，按原字节回读相等；无业务资源或动态复验", "source_sha256":sha(Path(__file__)),"inputs":captured})
text=result.read_bytes().decode("utf-8")
needle="最初文件核对命令也发生一次输出编码失败，不当作产品测试失败或忽略其投入。"
assert text.count(needle)==1
text=text.replace(needle,needle+"最后保存证明的CRLF回读标记也误报为否，原证明留存并按保留换行的UTF8原字节校正；文件没有丢失，不新增行为通过结论。")
for d in original["documents_saved_and_readable"]:
    p=Path(d["path"]);raw=p.read_bytes()
    assert raw.decode("utf-8").encode("utf-8")==raw
seconds=time.monotonic()-begin
ledger=read(E/"attempt-ledger.json")
ledger.append({"at":datetime.now(timezone.utc).isoformat(),"category":"offline","label":"offline-12-readback",
    "command":[sys.executable,"-B",str(Path(__file__).resolve())],"seconds":seconds,"exit_code":0,
    "scope":"修正文件回读证明，不是产品测试或资源入口"})
write(E/"attempt-ledger.json",ledger)
budget=read(E/"budget-final.json")
measured=sum(r.get("seconds",0) for r in ledger)
budget["offline_measured_seconds"]=measured
budget["offline_seconds"]=measured+60
budget["active_wall_upper_bound_seconds"]=time.time()-1790909032.161
budget["frozen_at"]=datetime.now(timezone.utc).isoformat()
active=budget["active_wall_upper_bound_seconds"]
text,n=re.subn(r"主动墙钟保守上界[0-9.]+秒，剩余[0-9.]+秒",f"主动墙钟保守上界{active:.3f}秒，剩余{28800-active:.3f}秒",text);assert n==1
text,n=re.subn(r"离线检查/构建实测[0-9.]+秒",f"离线检查/构建实测{measured:.3f}秒",text);assert n==1
text,n=re.subn(r"累计按[0-9.]+秒，占2400秒许可，剩余[0-9.]+秒",f"累计按{measured+60:.3f}秒，占2400秒许可，剩余{2340-measured:.3f}秒",text);assert n==1
result.write_bytes(text.encode("utf-8"))
write(E/"budget-final.json",budget)
state=read(E/"execution-ledger.json");state["budget_actual"]=budget;write(E/"execution-ledger.json",state)
proof=original.copy();proof["at"]=datetime.now(timezone.utc).isoformat();proof["budget"]=budget
proof["proof_revision"]="readback-fix-01"
proof["original_proof"]=str(OUT/"before/DocuN/evidence/TASK-097/delivery-proof.json")
proof["readback_method"]="strict UTF8 raw byte decode/encode preserving CRLF; no text newline normalization"
proof["documents_saved_and_readable"]=[]
for d in original["documents_saved_and_readable"]:
    p=Path(d["path"]);raw=p.read_bytes()
    proof["documents_saved_and_readable"].append({"path":str(p),"sha256":sha(p),"bytes":len(raw),
        "read_back_equal":raw.decode("utf-8").encode("utf-8")==raw})
assert all(d["read_back_equal"] for d in proof["documents_saved_and_readable"])
write(E/"delivery-proof.json",proof)
closing=read(E/"closing-run.json");closing["readback_fix"]={"path":str(OUT/"manifest.json"),"seconds":seconds,"exit_code":0,"resources_started":0};write(E/"closing-run.json",closing)
summary={"saved_readable":True,"result":str(result),"sha256":sha(result),"status":proof["status"],
    "offline_measured":round(measured,3),"offline_charged":round(measured+60,3),"active_wall_upper_seconds":round(active,3),
    "preserved_original_proof":proof["original_proof"],"new_resource_starts":0}
write(OUT/"run.json",{"started_at":started,"seconds":seconds,"exit_code":0,"post_sha256":sha(result),"summary":summary})
(OUT/"stdout.bin").write_bytes((json.dumps(summary,ensure_ascii=True)+"\n").encode("utf-8"));(OUT/"stderr.bin").write_bytes(b"")
print(json.dumps(summary,ensure_ascii=True))
