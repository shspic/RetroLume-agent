"""仅当前停止核查；不启动业务，不改历史回执，不从空PID查询推整树。"""
from pathlib import Path
import sys,json,subprocess,time
C01=Path(__file__).resolve().parents[1];EXEC=C01.parent;ROOT=EXEC.parents[3]
sys.path[:0]=[str(EXEC),str(ROOT/'backend')]
import control as c,runtime_control as rc
from app.preview.process import birth

def main(final=False):
    # Public API resolves the cached browser root; inventory covers Chrome and headless shell.
    code="console.log(JSON.stringify([require('playwright').chromium.executablePath()]))"
    resolved=subprocess.run(['node','-e',code],cwd=ROOT/'frontend',capture_output=True,timeout=10,check=True)
    programs=json.loads(resolved.stdout);assert len(programs)==1 and all(programs)
    cache_root=str(Path(programs[0]).parents[2]).lower()
    command="$ErrorActionPreference='Stop'; $rows=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,ExecutablePath); [pscustomobject]@{complete=$true;count=$rows.Count;rows=$rows} | ConvertTo-Json -Depth 4 -Compress"
    result=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,timeout=30,check=True)
    inventory=json.loads(result.stdout.decode('utf-8-sig'));assert inventory['complete'] and inventory['count']>20
    browser_rows=[r for r in inventory['rows'] if (r.get('ExecutablePath') or '').lower().startswith(cache_root+'\\') and Path(r.get('ExecutablePath') or '').name.lower() in ('chrome.exe','chrome-headless-shell.exe','headless_shell.exe')]
    descendants=[];parents={json.loads(p.read_text())['pid'] for p in C01.glob('browser-stop-*.json')} if final else {11104}
    for _ in range(12):
        new=[r for r in inventory['rows'] if r['ParentProcessId'] in parents and r['ProcessId'] not in parents]
        if not new:break
        descendants.extend(new);parents.update(r['ProcessId'] for r in new)
    pg=[rc.metadata(r['cid']) for r in c.state()['resources'] if r.get('kind')=='pg' and r.get('cid')]
    raw=subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; @(Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -in 15481,15482,15483,15484,15485,18118} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"],capture_output=True,timeout=20,check=True).stdout.decode('utf-8-sig').strip()
    listeners=json.loads(raw) if raw else []
    originals=[]
    for path in [*C01.glob('api-stop-*.json'),*C01.glob('browser-stop-*.json')]:
        value=json.loads(path.read_text());originals.append({'pid':value['pid'],'birth_before':value['birth_before'],'evidence':str(path.relative_to(ROOT))})
    if not final:originals=[r for r in originals if r['pid'] in (11104,4180)]
    births={str(r['pid']):birth(r['pid']) for r in originals}
    original_ended=all(births[str(r['pid'])]['state']=='exited' or (births[str(r['pid'])]['state']=='running' and type(births[str(r['pid'])].get('birth')) is int and births[str(r['pid'])]['birth']!=r['birth_before'].get('birth')) for r in originals)
    stopped=original_ended and not descendants and not browser_rows and not listeners and all(not r['running'] and r['pid']==0 for r in pg)
    proof={'sample':c.sample(),'all_stopped':stopped,'known_launch_births_now':births,'complete_Win32_Process_inventory':{'success':True,'rows':inventory['count'],'method':'successful full enumeration, adopted cached Chromium root and registered Node ancestry','chromium_paths':programs,'cache_root':cache_root,'matching_browser_processes':browser_rows,'node_descendants':descendants},'pg':pg,'listeners':listeners,'historical_browser_closed':'NOT_PROVED; original FAIL untouched','historical_cleanup':'UNCONFIRMED; original FAIL untouched','current_scope':'current absence of cached Chromium/Headless executables plus registered Node/API and full ancestry; does not reconstruct past close time','task_resources_started':0}
    proof['original_launch_receipts']=originals
    destination=C01/'quota-recovery'/(('final-stop-'+str(time.time_ns())+'.json') if final else 'current-stop.json')
    if destination.exists():raise RuntimeError('preserve_existing_stop_evidence')
    c.write(destination,proof)
    if final:c.write(C01/'final-resource-stop-binding.json',{'path':str(destination),'sha256':c.sha(destination.read_bytes()),'all_stopped':stopped})
    print(json.dumps({'all_stopped':stopped,'process_inventory_rows':inventory['count'],'chromium_matches':len(browser_rows),'descendants':len(descendants),'births':births,'pg_running':[r['name'] for r in pg if r['running']],'fixed_listeners':listeners},ensure_ascii=False))
    if not stopped:raise RuntimeError('current_stop_not_confirmed_read_exact_evidence')

if __name__=='__main__':main(final='--final' in sys.argv)
