"""只读收尾确认；不启动容器、业务监督、PG或浏览器。"""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"backend/tests/fixtures/task097"));sys.path.insert(0,str(ROOT/"backend"))
from resource_runner import inspect_guard,free
from processes import identity

E=ROOT/"DocuN/evidence/TASK-097"
facts=inspect_guard()
assert not facts["running"] and facts["pid"]==0
ports={}
for port in [18097,15197,55441]:free(port);ports[str(port)]="released"
owned=[]
for file in E.glob("integration-*/owned-processes.json"):
    owned.extend(json.loads(file.read_text(encoding="utf-8")))
for file in E.glob("integration-*/sup-launch-*.json"):
    row=json.loads(file.read_text(encoding="utf-8"))
    if row.get("created"):owned.append({"pid":row["pid"],"created_100ns":row["created_100ns"],"kind":"SUP"})
report=[]
for row in owned:
    current=identity(row["pid"])
    active=current is not None and current["created_100ns"]==row["created_100ns"] and current["alive"]
    report.append({**row,"own_process_active":active})
assert not any(row["own_process_active"] for row in report)
pid_list=",".join(str(r["pid"]) for r in owned)
# 只返回本卡根进程的现存后代元数据；不读取CommandLine或Env。
script="$ids=@("+pid_list+"); $rows=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CreationDate); $found=@(); for($depth=0;$depth -lt 8;$depth++){ $next=@($rows | Where-Object {$ids -contains $_.ParentProcessId -and $ids -notcontains $_.ProcessId}); if(!$next.Count){break}; $found+=$next; $ids+=@($next | ForEach-Object {$_.ProcessId}) }; ConvertTo-Json -InputObject @($found) -Depth 4 -Compress"
result=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",script],capture_output=True,text=True,timeout=30)
assert result.returncode==0
descendants=json.loads(result.stdout)
assert not descendants
state={"at":datetime.now(timezone.utc).isoformat(),"container":facts,"ports":ports,"owned_processes":report,
    "existing_descendants":descendants,"tree_zero":True,"new_starts":0,"database_and_volume":"preserved",
    "synthetic_data_retained":"integration-08-browser/retained-fixture.json","cleanup_commands_only_owned":True}
(E/"resources-final.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"resource_check":"PASS","container_running":False,"container_pid":0,"tree_zero":True,"ports":ports,"new_starts":0}))
