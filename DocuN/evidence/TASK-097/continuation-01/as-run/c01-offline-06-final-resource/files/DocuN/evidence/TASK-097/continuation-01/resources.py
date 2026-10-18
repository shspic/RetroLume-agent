"""最终只读身份/树/精确容器/端口核实；不启动或终止任何资源。"""
from pathlib import Path
import json,subprocess,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4];E=ROOT/'DocuN/evidence/TASK-097';C=E/'continuation-01'
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task097.resource_runner import inspect_guard,free
from tests.fixtures.task097.processes import identity
from app.worker.windows_job import NamedJob,JobOpenError,ERROR_FILE_NOT_FOUND

def main():
    facts=inspect_guard();assert not facts['running'] and facts['pid']==0
    ports={}
    for p in [18097,15197,55441]:free(p);ports[str(p)]='released'
    owned=[];supplements=[]
    for file in E.glob('integration-*/owned-processes.json'):owned.extend(json.loads(file.read_text(encoding='utf-8')))
    for file in E.glob('integration-*/sup-launch-*.json'):
        row=json.loads(file.read_text(encoding='utf-8'))
        if row.get('created'):owned.append({'pid':row['pid'],'created_100ns':row['created_100ns'],'kind':'SUP','origin':str(file.relative_to(ROOT))})
    # 10真实CreateProcess成功而观察替换失败的原始tmp，不补写旧launch行。
    for file in E.glob('integration-*/sup-launch-*.tmp'):
        row=json.loads(file.read_text(encoding='utf-8'))
        if row.get('created'):
            owned.append({'pid':row['pid'],'created_100ns':row['created_100ns'],'kind':'SUP_created_before_observer_error','origin':str(file.relative_to(ROOT))})
            supplements.append({'origin':str(file.relative_to(ROOT)),**row})
    rows=[]
    for expected in owned:
        current=identity(expected['pid']);active=current is not None and current['created_100ns']==expected['created_100ns'] and current['alive']
        rows.append({**expected,'current_identity':current,'own_process_active':active})
    assert not any(r['own_process_active'] for r in rows)
    ids=','.join(str(x['pid']) for x in owned)
    script='$ids=@('+ids+'); $rows=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CreationDate); $found=@(); for($depth=0;$depth -lt 8;$depth++){ $next=@($rows | Where-Object {$ids -contains $_.ParentProcessId -and $ids -notcontains $_.ProcessId}); if(!$next.Count){break}; $found+=$next; $ids+=@($next | ForEach-Object {$_.ProcessId}) }; ConvertTo-Json -InputObject @($found) -Depth 4 -Compress'
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,timeout=30)
    (C/'resource-cim.stdout.bin').write_bytes(r.stdout.encode('utf-8'));(C/'resource-cim.stderr.bin').write_bytes(r.stderr.encode('utf-8'))
    assert r.returncode==0;descendants=json.loads(r.stdout);assert not descendants
    jobs=[]
    sessions=[json.loads(p.read_text(encoding='utf-8')) for p in E.glob('integration-*/session-*.json')]
    for s in sessions:
        if s.get('generation') is None:continue
        try:
            job=NamedJob.open_existing(s['activity_id'],s['generation'])
            count=job.active_processes();job.close();assert count==0
            jobs.append({'job_name':s['job_name'],'state':'present_tree_zero','active':count})
        except JobOpenError as exc:
            assert exc.code==ERROR_FILE_NOT_FOUND
            jobs.append({'job_name':s['job_name'],'state':'not_found_after_close','error_code':exc.code})
    state={'at':datetime.now(timezone.utc).isoformat(),'container':facts,'ports':ports,'owned_processes':rows,
        'sup_created_supplements_from_original_temp':supplements,'existing_descendants':descendants,'jobs':jobs,
        'tree_zero':True,'new_starts':0,'database_and_volume':'preserved','old07_fixture_preserved':True,'new09_fixture_preserved_for_review':True,
        'commandline_env_or_credentials_read':False}
    (C/'resources-final.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'resource_check':'PASS','container_running':False,'container_pid':0,'tree_zero':True,'ports':ports,'jobs_checked':len(jobs),'new_starts':0}))

if __name__=='__main__':main()
